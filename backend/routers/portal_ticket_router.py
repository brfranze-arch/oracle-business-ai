from __future__ import annotations
from datetime import datetime
from pathlib import Path
import secrets, shutil
from fastapi import APIRouter, Depends, File, Form, UploadFile
from fastapi.responses import FileResponse, PlainTextResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from deps import get_current_user, get_db
from models import User
from portal_ticket_models import PortalTicket, PortalTicketComment, PortalTicketAttachment, PortalTicketEvent, PortalNotification
from tenant_models import TenantMember

router = APIRouter(prefix='/api/portal', tags=['Customer Portal Tickets'])
UPLOAD_ROOT = (Path(__file__).resolve().parents[1] / 'portal_ticket_uploads').resolve()
UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)
ALLOWED_EXTENSIONS = {'.pdf','.png','.jpg','.jpeg','.webp','.txt','.csv','.doc','.docx','.xls','.xlsx','.zip'}
MAX_FILE_SIZE = 10 * 1024 * 1024
CATEGORIES = {'SUPPORTO','BUG','COMMERCIALE','FEATURE_REQUEST','BILLING','SICUREZZA'}
PRIORITIES = {'BASSA','MEDIA','ALTA','CRITICA'}
STATUSES = {'APERTO','IN_LAVORAZIONE','IN_ATTESA_CLIENTE','RISOLTO','CHIUSO'}

class TicketCreate(BaseModel):
    subject: str = Field(min_length=3,max_length=180)
    description: str = Field(min_length=5,max_length=10000)
    category: str = 'SUPPORTO'
    priority: str = 'MEDIA'

class CommentCreate(BaseModel):
    body: str = Field(min_length=1,max_length=10000)

class TicketUpdate(BaseModel):
    status: str | None = None
    priority: str | None = None
    category: str | None = None
    assigned_to_user_id: int | None = None


def admin(user: User) -> bool:
    return (user.role or '').lower() in {'admin','owner','superadmin','support'}

def fmt(v): return v.isoformat() if v else None

def tenant_id(db: Session, user_id: int):
    row=db.query(TenantMember).filter(TenantMember.user_id==user_id).first()
    return row.tenant_id if row else None

def allowed(db: Session, ticket: PortalTicket, user: User):
    return admin(user) or ticket.user_id == user.id

def notify(db,user_id,title,message,link=''):
    db.add(PortalNotification(user_id=user_id,type='support',title=title,message=message,link=link))

def event(db,ticket,user,event_type,description):
    db.add(PortalTicketEvent(ticket_id=ticket.id,user_id=user.id,event_type=event_type,description=description))

def serialize(db,t):
    comments=db.query(PortalTicketComment).filter(PortalTicketComment.ticket_id==t.id, PortalTicketComment.internal==False).order_by(PortalTicketComment.created_at.asc()).all()
    attachments=db.query(PortalTicketAttachment).filter(PortalTicketAttachment.ticket_id==t.id).order_by(PortalTicketAttachment.created_at.asc()).all()
    events=db.query(PortalTicketEvent).filter(PortalTicketEvent.ticket_id==t.id).order_by(PortalTicketEvent.created_at.asc()).all()
    return {'id':t.id,'code':t.code,'subject':t.subject,'description':t.description,'category':t.category,'priority':t.priority,'status':t.status,'assigned_to_user_id':t.assigned_to_user_id,'created_at':fmt(t.created_at),'updated_at':fmt(t.updated_at),'closed_at':fmt(t.closed_at),
      'comments':[{'id':x.id,'author_name':x.author_name,'body':x.body,'created_at':fmt(x.created_at)} for x in comments],
      'attachments':[{'id':x.id,'original_name':x.original_name,'content_type':x.content_type,'size_bytes':x.size_bytes,'created_at':fmt(x.created_at),'download_url':f'/api/portal/tickets/{t.id}/attachments/{x.id}'} for x in attachments],
      'events':[{'id':x.id,'event_type':x.event_type,'description':x.description,'created_at':fmt(x.created_at)} for x in events]}

@router.get('/tickets/meta')
def metadata(current_user: User=Depends(get_current_user)):
    if not current_user: return {'error':'Non autenticato'}
    return {'categories':sorted(CATEGORIES),'priorities':sorted(PRIORITIES),'statuses':sorted(STATUSES),'max_attachment_bytes':MAX_FILE_SIZE,'allowed_extensions':sorted(ALLOWED_EXTENSIONS)}

@router.get('/tickets')
def list_tickets(status: str|None=None, db:Session=Depends(get_db), current_user:User=Depends(get_current_user)):
    if not current_user: return {'error':'Non autenticato'}
    q=db.query(PortalTicket)
    if not admin(current_user): q=q.filter(PortalTicket.user_id==current_user.id)
    if status: q=q.filter(PortalTicket.status==status.upper())
    return [serialize(db,x) for x in q.order_by(PortalTicket.updated_at.desc()).limit(200).all()]

@router.post('/tickets')
def create_ticket(payload:TicketCreate, db:Session=Depends(get_db), current_user:User=Depends(get_current_user)):
    if not current_user: return {'error':'Non autenticato'}
    category=payload.category.upper(); priority=payload.priority.upper()
    if category not in CATEGORIES or priority not in PRIORITIES: return {'error':'Categoria o priorità non valida'}
    row=PortalTicket(code=f'O360-{datetime.utcnow():%Y%m%d}-{secrets.token_hex(3).upper()}',user_id=current_user.id,tenant_id=tenant_id(db,current_user.id),subject=payload.subject.strip(),description=payload.description.strip(),category=category,priority=priority)
    db.add(row); db.flush(); event(db,row,current_user,'CREATO','Ticket creato dal cliente'); notify(db,current_user.id,'Ticket creato',f'{row.code} · {row.subject}',f'tickets:{row.id}'); db.commit(); db.refresh(row)
    return {'message':'Ticket creato','ticket':serialize(db,row)}

@router.get('/tickets/{ticket_id}')
def get_ticket(ticket_id:int, db:Session=Depends(get_db), current_user:User=Depends(get_current_user)):
    if not current_user: return {'error':'Non autenticato'}
    row=db.query(PortalTicket).filter(PortalTicket.id==ticket_id).first()
    if not row or not allowed(db,row,current_user): return {'error':'Ticket non trovato'}
    return serialize(db,row)

@router.post('/tickets/{ticket_id}/comments')
def add_comment(ticket_id:int,payload:CommentCreate,db:Session=Depends(get_db),current_user:User=Depends(get_current_user)):
    if not current_user:return {'error':'Non autenticato'}
    row=db.query(PortalTicket).filter(PortalTicket.id==ticket_id).first()
    if not row or not allowed(db,row,current_user):return {'error':'Ticket non trovato'}
    c=PortalTicketComment(ticket_id=row.id,user_id=current_user.id,author_name=current_user.name or current_user.email,body=payload.body.strip())
    db.add(c); row.updated_at=datetime.utcnow(); event(db,row,current_user,'COMMENTO','Nuovo commento aggiunto'); notify(db,row.user_id,'Nuovo aggiornamento ticket',f'{row.code} ha un nuovo commento',f'tickets:{row.id}'); db.commit(); db.refresh(row)
    return {'message':'Commento aggiunto','ticket':serialize(db,row)}

@router.post('/tickets/{ticket_id}/attachments')
def upload_attachment(ticket_id:int,file:UploadFile=File(...),db:Session=Depends(get_db),current_user:User=Depends(get_current_user)):
    if not current_user:return {'error':'Non autenticato'}
    row=db.query(PortalTicket).filter(PortalTicket.id==ticket_id).first()
    if not row or not allowed(db,row,current_user):return {'error':'Ticket non trovato'}
    original=Path(file.filename or 'allegato').name; ext=Path(original).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:return {'error':'Formato allegato non consentito'}
    stored=f'{ticket_id}_{secrets.token_hex(16)}{ext}'; path=(UPLOAD_ROOT/stored).resolve()
    size=0
    with path.open('wb') as out:
        while chunk:=file.file.read(1024*1024):
            size+=len(chunk)
            if size>MAX_FILE_SIZE:
                out.close(); path.unlink(missing_ok=True); return {'error':'Allegato superiore a 10 MB'}
            out.write(chunk)
    a=PortalTicketAttachment(ticket_id=row.id,user_id=current_user.id,original_name=original,stored_name=stored,storage_path=str(path),content_type=file.content_type or 'application/octet-stream',size_bytes=size)
    db.add(a); row.updated_at=datetime.utcnow(); event(db,row,current_user,'ALLEGATO',f'Allegato caricato: {original}'); db.commit(); db.refresh(row)
    return {'message':'Allegato caricato','ticket':serialize(db,row)}

@router.get('/tickets/{ticket_id}/attachments/{attachment_id}')
def download_attachment(ticket_id:int,attachment_id:int,db:Session=Depends(get_db),current_user:User=Depends(get_current_user)):
    if not current_user:return PlainTextResponse('Non autenticato',status_code=401)
    row=db.query(PortalTicket).filter(PortalTicket.id==ticket_id).first()
    if not row or not allowed(db,row,current_user):return PlainTextResponse('Ticket non trovato',status_code=404)
    a=db.query(PortalTicketAttachment).filter(PortalTicketAttachment.id==attachment_id,PortalTicketAttachment.ticket_id==ticket_id).first()
    if not a:return PlainTextResponse('Allegato non trovato',status_code=404)
    path=Path(a.storage_path).resolve()
    if UPLOAD_ROOT not in path.parents or not path.is_file():return PlainTextResponse('File non disponibile',status_code=404)
    return FileResponse(str(path),filename=a.original_name,media_type=a.content_type)

@router.patch('/tickets/{ticket_id}')
def update_ticket(ticket_id:int,payload:TicketUpdate,db:Session=Depends(get_db),current_user:User=Depends(get_current_user)):
    if not current_user:return {'error':'Non autenticato'}
    row=db.query(PortalTicket).filter(PortalTicket.id==ticket_id).first()
    if not row or not allowed(db,row,current_user):return {'error':'Ticket non trovato'}
    if not admin(current_user) and payload.status not in {None,'CHIUSO'}:return {'error':'Operazione riservata al supporto'}
    changes=[]
    if payload.status:
        value=payload.status.upper()
        if value not in STATUSES:return {'error':'Stato non valido'}
        row.status=value; row.closed_at=datetime.utcnow() if value=='CHIUSO' else None; changes.append(f'stato={value}')
    if admin(current_user) and payload.priority:
        value=payload.priority.upper()
        if value not in PRIORITIES:return {'error':'Priorità non valida'}
        row.priority=value;changes.append(f'priorità={value}')
    if admin(current_user) and payload.category:
        value=payload.category.upper()
        if value not in CATEGORIES:return {'error':'Categoria non valida'}
        row.category=value;changes.append(f'categoria={value}')
    if admin(current_user) and payload.assigned_to_user_id is not None: row.assigned_to_user_id=payload.assigned_to_user_id;changes.append('assegnazione aggiornata')
    row.updated_at=datetime.utcnow(); event(db,row,current_user,'AGGIORNATO',', '.join(changes) or 'Ticket aggiornato'); notify(db,row.user_id,'Ticket aggiornato',f'{row.code}: {", ".join(changes)}',f'tickets:{row.id}'); db.commit();db.refresh(row)
    return {'message':'Ticket aggiornato','ticket':serialize(db,row)}

@router.get('/notifications')
def notifications(db:Session=Depends(get_db),current_user:User=Depends(get_current_user)):
    if not current_user:return {'error':'Non autenticato'}
    rows=db.query(PortalNotification).filter(PortalNotification.user_id==current_user.id).order_by(PortalNotification.created_at.desc()).limit(100).all()
    return [{'id':x.id,'type':x.type,'title':x.title,'message':x.message,'link':x.link,'read':x.read,'created_at':fmt(x.created_at)} for x in rows]

@router.post('/notifications/read-all')
def read_all(db:Session=Depends(get_db),current_user:User=Depends(get_current_user)):
    if not current_user:return {'error':'Non autenticato'}
    db.query(PortalNotification).filter(PortalNotification.user_id==current_user.id).update({'read':True});db.commit();return {'message':'Notifiche lette'}

@router.post('/notifications/{notification_id}/read')
def read_one(notification_id:int,db:Session=Depends(get_db),current_user:User=Depends(get_current_user)):
    if not current_user:return {'error':'Non autenticato'}
    row=db.query(PortalNotification).filter(PortalNotification.id==notification_id,PortalNotification.user_id==current_user.id).first()
    if not row:return {'error':'Notifica non trovata'}
    row.read=True;db.commit();return {'message':'Notifica letta'}

from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text
from database import Base

class PortalTicket(Base):
    __tablename__ = 'portal_tickets'
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(Integer, index=True, nullable=False)
    tenant_id = Column(Integer, index=True, nullable=True)
    subject = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String, default='SUPPORTO', index=True)
    priority = Column(String, default='MEDIA', index=True)
    status = Column(String, default='APERTO', index=True)
    assigned_to_user_id = Column(Integer, index=True, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    closed_at = Column(DateTime, nullable=True)

class PortalTicketComment(Base):
    __tablename__ = 'portal_ticket_comments'
    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, index=True, nullable=False)
    user_id = Column(Integer, index=True, nullable=False)
    author_name = Column(String, default='')
    body = Column(Text, nullable=False)
    internal = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class PortalTicketAttachment(Base):
    __tablename__ = 'portal_ticket_attachments'
    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, index=True, nullable=False)
    comment_id = Column(Integer, index=True, nullable=True)
    user_id = Column(Integer, index=True, nullable=False)
    original_name = Column(String, nullable=False)
    stored_name = Column(String, unique=True, nullable=False)
    storage_path = Column(Text, nullable=False)
    content_type = Column(String, default='application/octet-stream')
    size_bytes = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

class PortalTicketEvent(Base):
    __tablename__ = 'portal_ticket_events'
    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, index=True, nullable=False)
    user_id = Column(Integer, index=True, nullable=False)
    event_type = Column(String, nullable=False)
    description = Column(Text, default='')
    created_at = Column(DateTime, default=datetime.utcnow)

class PortalNotification(Base):
    __tablename__ = 'portal_notifications'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    type = Column(String, default='support')
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    link = Column(String, default='')
    read = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

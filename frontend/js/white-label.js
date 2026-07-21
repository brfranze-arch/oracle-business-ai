window.O360Brand = {tenantId:0};
function brandTenantId(){return Number(localStorage.getItem("oracle_tenant_id")||0)}
function applyO360Brand(b){
  if(!b||b.error)return;
  window.O360Brand={...b,tenantId:brandTenantId()};
  const root=document.documentElement;
  root.style.setProperty("--brand-primary",b.primary_color||"#2563EB");
  root.style.setProperty("--brand-secondary",b.secondary_color||"#0F172A");
  root.style.setProperty("--brand-accent",b.accent_color||"#22C55E");
  root.style.setProperty("--brand-background",b.background_color||"#F8FAFC");
  document.title=`${b.brand_name||"Orizzonte360"} — Piattaforma Enterprise`;
  document.querySelectorAll("[data-brand-name]").forEach(x=>x.textContent=b.brand_name||"Orizzonte360");
  const logo=document.getElementById("dynamicBrandLogo");
  if(logo&&b.logo_url){logo.src=b.logo_url;logo.hidden=false}
  let icon=document.querySelector('link[rel="icon"]'); if(!icon){icon=document.createElement("link");icon.rel="icon";document.head.appendChild(icon)}
  if(b.favicon_url)icon.href=b.favicon_url;
}
async function loadO360Brand(){
  try{const tid=brandTenantId();const r=await fetch(`${API}/api/white-label/public/resolve?tenant_id=${tid}&portal_type=app&hostname=${encodeURIComponent(location.hostname)}`);applyO360Brand(await r.json())}catch(e){console.warn("White Label non disponibile",e)}
}
async function renderWhiteLabel(){
  setPageTitle("White Label");
  setContent(`<div class="card"><h2>🎨 White Label Manager</h2><p>Personalizza il tenant selezionato. I portali useranno automaticamente questo brand.</p><div id="wlMessage"></div><div class="grid-2"><label>Nome brand<input id="wlName"></label><label>Tagline<input id="wlTagline"></label><label>Logo URL<input id="wlLogo"></label><label>Favicon URL<input id="wlFavicon"></label><label>Colore primario<input id="wlPrimary" type="color"></label><label>Colore secondario<input id="wlSecondary" type="color"></label><label>Colore accento<input id="wlAccent" type="color"></label><label>Sfondo<input id="wlBackground" type="color"></label><label>Email supporto<input id="wlEmail"></label><label>Telefono supporto<input id="wlPhone"></label><label>Sito web<input id="wlWebsite"></label><label>Footer<input id="wlFooter"></label><label>Privacy URL<input id="wlPrivacy"></label><label>Termini URL<input id="wlTerms"></label></div><button onclick="saveWhiteLabel()">Salva branding</button><hr><h3>🌐 Domini personalizzati</h3><div class="grid-2"><input id="wlDomain" placeholder="app.partner.it"><select id="wlPortal"><option value="app">App</option><option value="customer">Customer Portal</option><option value="partner">Partner Portal</option><option value="login">Login</option><option value="website">Website</option></select></div><button onclick="addWhiteLabelDomain()">Aggiungi dominio</button><div id="wlDomains"></div></div>`);
  const b=await apiGet("/api/white-label/brand"); if(b.error){showError("wlMessage",b.error);return}
  const map={wlName:"brand_name",wlTagline:"tagline",wlLogo:"logo_url",wlFavicon:"favicon_url",wlPrimary:"primary_color",wlSecondary:"secondary_color",wlAccent:"accent_color",wlBackground:"background_color",wlEmail:"support_email",wlPhone:"support_phone",wlWebsite:"website_url",wlFooter:"footer_text",wlPrivacy:"privacy_url",wlTerms:"terms_url"};Object.entries(map).forEach(([id,k])=>document.getElementById(id).value=b[k]||"");loadWhiteLabelDomains();
}
async function saveWhiteLabel(){
 const body={brand_name:wlName.value,tagline:wlTagline.value,logo_url:wlLogo.value,favicon_url:wlFavicon.value,primary_color:wlPrimary.value,secondary_color:wlSecondary.value,accent_color:wlAccent.value,background_color:wlBackground.value,support_email:wlEmail.value,support_phone:wlPhone.value,website_url:wlWebsite.value,footer_text:wlFooter.value,privacy_url:wlPrivacy.value,terms_url:wlTerms.value,hide_powered_by:false,enabled:true};
 const r=await fetch(`${API}/api/white-label/brand`,{method:"PUT",headers:{...authHeaders(),"Content-Type":"application/json"},body:JSON.stringify(body)});const d=await r.json();document.getElementById("wlMessage").innerHTML=`<div class="result">${safeValue(d.message||d.error)}</div>`;if(!d.error){applyO360Brand(d.brand);}
}
async function loadWhiteLabelDomains(){const d=await apiGet("/api/white-label/domains");if(d.error){showError("wlDomains",d.error);return}document.getElementById("wlDomains").innerHTML=(d.length?d.map(x=>`<div class="result"><b>${safeValue(x.hostname)}</b> · ${safeValue(x.portal_type)} · ${x.verified?"✅ Verificato":"⏳ Da verificare"}<br><small>TXT: ${safeValue(x.dns_record)}</small>${!x.verified?`<br><button onclick="verifyWhiteLabelDomain(${x.id},'${x.verification_token}')">Verifica token</button>`:""} <button onclick="deleteWhiteLabelDomain(${x.id})">Rimuovi</button></div>`).join(""):"<p>Nessun dominio configurato.</p>")}
async function addWhiteLabelDomain(){const r=await fetch(`${API}/api/white-label/domains`,{method:"POST",headers:{...authHeaders(),"Content-Type":"application/json"},body:JSON.stringify({hostname:wlDomain.value,portal_type:wlPortal.value})});const d=await r.json();alert(d.message||d.error);loadWhiteLabelDomains()}
async function verifyWhiteLabelDomain(id,t){const r=await fetch(`${API}/api/white-label/domains/${id}/verify?confirmation_token=${encodeURIComponent(t)}`,{method:"POST",headers:authHeaders()});const d=await r.json();alert(d.message||d.error);loadWhiteLabelDomains()}
async function deleteWhiteLabelDomain(id){const r=await fetch(`${API}/api/white-label/domains/${id}`,{method:"DELETE",headers:authHeaders()});const d=await r.json();alert(d.message||d.error);loadWhiteLabelDomains()}
document.addEventListener("DOMContentLoaded",loadO360Brand);

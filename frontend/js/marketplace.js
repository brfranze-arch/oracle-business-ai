async function marketplaceRequest(path, options={}) {
  try {
    const headers=authHeaders();
    if(options.body){headers["Content-Type"]="application/json";options.body=JSON.stringify(options.body);}
    const res=await fetch(API+path,{...options,headers});
    const data=await res.json();
    if(!res.ok) return {error:data.detail||data.error||`Errore ${res.status}`};
    return data;
  } catch(e){return {error:"Backend Marketplace non raggiungibile"};}
}
function marketMoney(v,c="EUR"){return Number(v||0).toLocaleString("it-IT",{style:"currency",currency:c});}
async function renderMarketplace(){
  setPageTitle("Marketplace"); setContent('<div class="card"><h2>Marketplace Orizzonte360</h2><p>Caricamento catalogo...</p></div>');
  const [metrics,categories,modules]=await Promise.all([marketplaceRequest('/api/marketplace/admin/metrics'),marketplaceRequest('/api/marketplace/categories'),marketplaceRequest('/api/marketplace/admin/modules')]);
  if(modules.error){setContent(`<div class="card"><h2>Marketplace</h2><div class="result">${modules.error}</div></div>`);return;}
  setContent(`
    <div class="dashboard-grid">
      <div class="card"><h3>Moduli</h3><div class="metric-value">${metrics.modules||0}</div></div>
      <div class="card"><h3>Pubblicati</h3><div class="metric-value">${metrics.published||0}</div></div>
      <div class="card"><h3>Installazioni attive</h3><div class="metric-value">${metrics.installations_active||0}</div></div>
    </div>
    <div class="card"><div class="market-head"><div><h2>Catalogo moduli</h2><p>Gestione amministrativa del Marketplace Core.</p></div><button id="marketNew">+ Nuovo modulo</button></div>
    <div class="table-wrap"><table><thead><tr><th>Modulo</th><th>Categoria</th><th>Prezzo</th><th>Piano</th><th>Stato</th><th>Installazioni</th></tr></thead><tbody>${modules.map(m=>`<tr><td><b>${m.icon} ${m.name}</b><br><small>${m.slug} · v${m.version}</small></td><td>${m.category?.name||'—'}</td><td>${m.billing_type==='FREE'?'Gratis':marketMoney(m.price,m.currency)}</td><td>${m.required_plan}</td><td><span class="badge badge-blue">${m.status}</span></td><td>${m.install_count}</td></tr>`).join('')}</tbody></table></div></div>`);
  document.getElementById('marketNew').onclick=()=>openMarketplaceForm(categories);
}
function openMarketplaceForm(categories){
  const html=`<div class="card"><h2>Nuovo modulo Marketplace</h2><div class="form-grid">
    <input id="mmName" placeholder="Nome modulo"><input id="mmSlug" placeholder="slug-modulo">
    <select id="mmCategory">${categories.map(c=>`<option value="${c.id}">${c.name}</option>`).join('')}</select>
    <input id="mmIcon" placeholder="Icona" value="◆"><input id="mmVersion" value="1.0.0" placeholder="Versione">
    <input id="mmShort" placeholder="Descrizione breve"><textarea id="mmDescription" placeholder="Descrizione completa"></textarea>
    <select id="mmBilling"><option>FREE</option><option>ONE_TIME</option><option>MONTHLY</option></select><input id="mmPrice" type="number" min="0" step="0.01" value="0">
    <select id="mmPlan"><option>FREE</option><option>PROFESSIONAL</option><option>BUSINESS</option><option>ENTERPRISE</option></select>
    <button id="mmSave">Salva e pubblica</button><button onclick="renderMarketplace()">Annulla</button></div><div id="mmResult"></div></div>`;
  setContent(html);
  document.getElementById('mmSave').onclick=async()=>{const payload={name:mmName.value,slug:mmSlug.value,category_id:Number(mmCategory.value),icon:mmIcon.value,version:mmVersion.value,short_description:mmShort.value,description:mmDescription.value,billing_type:mmBilling.value,price:Number(mmPrice.value),required_plan:mmPlan.value,currency:'EUR',status:'PUBLISHED',featured:false,active:true};const r=await marketplaceRequest('/api/marketplace/admin/modules',{method:'POST',body:payload});document.getElementById('mmResult').innerHTML=`<div class="result">${r.error||r.message}</div>`;if(!r.error)setTimeout(renderMarketplace,700);};
}

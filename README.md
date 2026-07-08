# Oracle Business AI RC1 Patch 02 — Digital Twin Engine

Patch incrementale sicura. Non sostituisce cartelle complete e non cancella file.

## Cosa aggiunge
- Backend Digital Twin Engine
- Modello `DigitalTwinSnapshot`
- Router FastAPI `/api/digital-twin/...`
- Frontend Digital Twin nei Reports
- Script `apply_patch.py` per aggiornare automaticamente `main.py`, `create_tables.py`, `index.html`, `reports.js`

## Installazione
1. Estrai questo ZIP nella root del progetto `oracle_business_ai`, dove ci sono `backend/` e `frontend/`.
2. Esegui:

```powershell
cd C:\Users\brfra\OneDrive\Desktop\oracle_business_ai
python apply_patch.py
```

3. Crea le tabelle:

```powershell
cd backend
.\venv\Scripts\Activate.ps1
python create_tables.py
uvicorn main:app --reload
```

## Test locale
- Apri frontend locale.
- Vai in Reports.
- Clicca `Digital Twin`.
- Clicca `Storico Digital Twin`.

Serve piano BUSINESS o ENTERPRISE, perché usa il permesso `predictive`.

## Deploy
```powershell
cd C:\Users\brfra\OneDrive\Desktop\oracle_business_ai
git add .
git commit -m "RC1 Patch 02 Digital Twin Engine"
git push
```

Poi su Render backend:
`Manual Deploy → Deploy latest commit`.

Frontend Render si aggiorna automaticamente.

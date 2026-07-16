from __future__ import annotations

import hashlib
from pathlib import Path

from sqlalchemy.orm import Session

from portal_license_models import PortalDownload, PortalRelease


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def seed_portal_catalog(db: Session) -> None:
    base_dir = Path(__file__).resolve().parent / "portal_downloads"
    base_dir.mkdir(parents=True, exist_ok=True)

    catalog = [
        {
            "slug": "quick-start-rc1",
            "title": "Guida rapida Orizzonte360 RC1",
            "description": "Primo accesso, tenant, azienda, dashboard e flusso consigliato.",
            "category": "DOCUMENTATION",
            "file_name": "Orizzonte360_Guida_Rapida_RC1.txt",
            "storage_path": "quick_start_rc1.txt",
            "version": "1.0.0-RC1",
            "min_plan": "FREE",
            "required_edition": "ANY",
        },
        {
            "slug": "release-notes-rc1",
            "title": "Release Notes 1.0.0-RC1",
            "description": "Novità, moduli inclusi e note di compatibilità.",
            "category": "RELEASE",
            "file_name": "Orizzonte360_Release_Notes_1.0.0-RC1.md",
            "storage_path": "release_notes_1_0_0_rc1.md",
            "version": "1.0.0-RC1",
            "min_plan": "FREE",
            "required_edition": "ANY",
        },
        {
            "slug": "enterprise-deployment-checklist",
            "title": "Checklist distribuzione Enterprise",
            "description": "Controlli preliminari per installazioni Enterprise e Docker.",
            "category": "ENTERPRISE",
            "file_name": "Orizzonte360_Enterprise_Deployment_Checklist.txt",
            "storage_path": "enterprise_deployment_checklist.txt",
            "version": "1.0.0",
            "min_plan": "ENTERPRISE",
            "required_edition": "ANY",
        },
    ]

    for item in catalog:
        path = base_dir / item["storage_path"]
        if not path.exists():
            continue
        existing = db.query(PortalDownload).filter(PortalDownload.slug == item["slug"]).first()
        values = {
            **item,
            "storage_path": str(path),
            "size_bytes": path.stat().st_size,
            "checksum_sha256": _sha256(path),
            "active": True,
        }
        if existing:
            for key, value in values.items():
                setattr(existing, key, value)
        else:
            db.add(PortalDownload(**values))

    releases = [
        {
            "version": "1.0.0-RC1",
            "channel": "stable",
            "status": "available",
            "title": "Orizzonte360 1.0.0 Release Candidate",
            "summary": "Release Candidate con Billing SaaS, Multi Tenant, OpenAI, OSINT, Predictive AI, Autonomous Agents, Digital Twin e Import Enterprise.",
            "changelog": "- Customer Portal con autenticazione reale\n- License Manager e download protetti\n- Release Center integrato\n- Digital Twin e storico\n- Import Excel multi-foglio",
            "min_plan": "FREE",
        },
        {
            "version": "0.9.5",
            "channel": "previous",
            "status": "archived",
            "title": "Orizzonte360 0.9.5",
            "summary": "Billing SaaS, multi-tenant e OpenAI Advisor.",
            "changelog": "- Stripe Checkout e Customer Portal\n- Permessi per piano\n- Tenant e workspace",
            "min_plan": "FREE",
        },
    ]
    for item in releases:
        existing = db.query(PortalRelease).filter(PortalRelease.version == item["version"]).first()
        if existing:
            for key, value in item.items():
                setattr(existing, key, value)
        else:
            db.add(PortalRelease(**item))
    db.commit()

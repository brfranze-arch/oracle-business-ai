from __future__ import annotations

from datetime import datetime
from typing import Any

import pandas as pd
from sqlalchemy.orm import Session

from models import (
    Revenue,
    Customer,
    ComplianceItem,
    CyberAsset,
    CyberFinding,
    CyberThreat,
    ImportJob,
)


def normalize_column(value: Any) -> str:
    return (
        str(value)
        .strip()
        .lower()
        .replace(" ", "_")
        .replace("-", "_")
    )


def normalize_text(value: Any, default: str = "") -> str:
    if value is None or pd.isna(value):
        return default

    return str(value).strip()


def normalize_float(value: Any, default: float = 0.0) -> float:
    if value is None or pd.isna(value):
        return default

    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def normalize_int(value: Any, default: int = 0) -> int:
    if value is None or pd.isna(value):
        return default

    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def normalize_date(value: Any) -> str:
    if value is None or pd.isna(value):
        return ""

    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d")

    try:
        parsed = pd.to_datetime(value)
        return parsed.strftime("%Y-%m-%d")
    except Exception:
        return str(value).strip()


def normalize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    copy = df.copy()
    copy.columns = [normalize_column(column) for column in copy.columns]
    return copy


def find_customer_by_name(
    db: Session,
    company_id: int,
    name: str,
) -> Customer | None:
    if not name:
        return None

    return (
        db.query(Customer)
        .filter(
            Customer.company_id == company_id,
            Customer.name == name,
        )
        .first()
    )


def get_or_create_customer(
    db: Session,
    company_id: int,
    name: str,
    email: str = "",
    phone: str = "",
    customer_type: str = "import",
    notes: str = "",
) -> Customer | None:
    clean_name = name.strip()

    if not clean_name:
        return None

    customer = find_customer_by_name(
        db=db,
        company_id=company_id,
        name=clean_name,
    )

    if customer:
        if email and not customer.email:
            customer.email = email

        if phone and not customer.phone:
            customer.phone = phone

        if customer_type and not customer.customer_type:
            customer.customer_type = customer_type

        if notes and not customer.notes:
            customer.notes = notes

        return customer

    customer = Customer(
        company_id=company_id,
        name=clean_name,
        email=email,
        phone=phone,
        customer_type=customer_type or "import",
        notes=notes or "Creato tramite Import Enterprise",
    )

    db.add(customer)
    db.flush()

    return customer


def import_customers(
    db: Session,
    company_id: int,
    df: pd.DataFrame,
) -> dict:
    df = normalize_dataframe(df)

    created = 0
    updated = 0
    errors: list[str] = []

    for index, row in df.iterrows():
        try:
            name = normalize_text(row.get("name") or row.get("customer"))

            if not name:
                errors.append(
                    f"Customers riga {index + 2}: nome cliente mancante"
                )
                continue

            existing = find_customer_by_name(
                db=db,
                company_id=company_id,
                name=name,
            )

            customer = get_or_create_customer(
                db=db,
                company_id=company_id,
                name=name,
                email=normalize_text(row.get("email")),
                phone=normalize_text(row.get("phone")),
                customer_type=normalize_text(
                    row.get("customer_type")
                    or row.get("sector"),
                    "import",
                ),
                notes=normalize_text(
                    row.get("notes"),
                    "Import Enterprise",
                ),
            )

            if customer is None:
                errors.append(
                    f"Customers riga {index + 2}: cliente non valido"
                )
                continue

            if existing:
                updated += 1
            else:
                created += 1

        except Exception as exc:
            errors.append(
                f"Customers riga {index + 2}: {str(exc)}"
            )

    return {
        "processed": len(df),
        "created": created,
        "updated": updated,
        "errors": errors,
    }


def import_revenues(
    db: Session,
    company_id: int,
    df: pd.DataFrame,
) -> dict:
    df = normalize_dataframe(df)

    created = 0
    errors: list[str] = []

    for index, row in df.iterrows():
        try:
            amount = normalize_float(
                row.get("amount")
                or row.get("importo")
                or row.get("totale")
            )

            if amount <= 0:
                errors.append(
                    f"Revenues riga {index + 2}: importo non valido"
                )
                continue

            customer_name = normalize_text(
                row.get("customer")
                or row.get("cliente")
                or row.get("customer_name")
            )

            customer = get_or_create_customer(
                db=db,
                company_id=company_id,
                name=customer_name,
                notes="Creato automaticamente da Revenues",
            )

            revenue = Revenue(
                company_id=company_id,
                customer_id=customer.id if customer else None,
                amount=amount,
                payment_method=normalize_text(
                    row.get("payment_method")
                    or row.get("metodo_pagamento")
                    or row.get("metodo"),
                    "digitale",
                ).lower(),
                category=normalize_text(
                    row.get("category")
                    or row.get("categoria"),
                    "import",
                ).lower(),
                note=normalize_text(
                    row.get("note")
                    or row.get("description")
                    or row.get("descrizione"),
                    "Import Enterprise",
                ),
            )

            db.add(revenue)
            created += 1

        except Exception as exc:
            errors.append(
                f"Revenues riga {index + 2}: {str(exc)}"
            )

    return {
        "processed": len(df),
        "created": created,
        "errors": errors,
    }


def import_compliance(
    db: Session,
    company_id: int,
    df: pd.DataFrame,
) -> dict:
    df = normalize_dataframe(df)

    created = 0
    errors: list[str] = []

    for index, row in df.iterrows():
        try:
            title = normalize_text(row.get("title"))

            if not title:
                errors.append(
                    f"Compliance riga {index + 2}: titolo mancante"
                )
                continue

            item = ComplianceItem(
                company_id=company_id,
                title=title,
                item_type=normalize_text(
                    row.get("item_type")
                    or row.get("type")
                    or row.get("category"),
                    "generale",
                ),
                status=normalize_text(
                    row.get("status"),
                    "pendente",
                ).lower(),
                due_date=normalize_date(row.get("due_date")),
                notes=normalize_text(
                    row.get("notes")
                    or row.get("priority"),
                    "Import Enterprise",
                ),
            )

            db.add(item)
            created += 1

        except Exception as exc:
            errors.append(
                f"Compliance riga {index + 2}: {str(exc)}"
            )

    return {
        "processed": len(df),
        "created": created,
        "errors": errors,
    }


def import_cyber_assets(
    db: Session,
    company_id: int,
    df: pd.DataFrame,
) -> dict:
    df = normalize_dataframe(df)

    created = 0
    errors: list[str] = []

    for index, row in df.iterrows():
        try:
            value = normalize_text(
                row.get("value")
                or row.get("hostname")
                or row.get("asset_name")
            )

            if not value:
                errors.append(
                    f"CyberAssets riga {index + 2}: valore asset mancante"
                )
                continue

            asset = CyberAsset(
                company_id=company_id,
                asset_type=normalize_text(
                    row.get("asset_type"),
                    "unknown",
                ).lower(),
                value=value,
                provider=normalize_text(
                    row.get("provider"),
                    "unknown",
                ),
                technology_stack=normalize_text(
                    row.get("technology_stack"),
                    "",
                ),
                notes=normalize_text(
                    row.get("notes")
                    or row.get("criticality"),
                    "Import Enterprise",
                ),
            )

            db.add(asset)
            created += 1

        except Exception as exc:
            errors.append(
                f"CyberAssets riga {index + 2}: {str(exc)}"
            )

    return {
        "processed": len(df),
        "created": created,
        "errors": errors,
    }


def import_cyber_findings(
    db: Session,
    company_id: int,
    df: pd.DataFrame,
) -> dict:
    df = normalize_dataframe(df)

    created = 0
    errors: list[str] = []

    assets = (
        db.query(CyberAsset)
        .filter(CyberAsset.company_id == company_id)
        .order_by(CyberAsset.id.asc())
        .all()
    )

    default_asset_id = assets[0].id if assets else 0

    for index, row in df.iterrows():
        try:
            title = normalize_text(row.get("title"))

            if not title:
                errors.append(
                    f"CyberFindings riga {index + 2}: titolo mancante"
                )
                continue

            finding = CyberFinding(
                company_id=company_id,
                scan_id=0,
                asset_id=normalize_int(
                    row.get("asset_id"),
                    default_asset_id,
                ),
                title=title,
                category=normalize_text(
                    row.get("category"),
                    "general",
                ),
                severity=normalize_text(
                    row.get("severity"),
                    "medium",
                ).lower(),
                description=normalize_text(
                    row.get("description"),
                    "Finding importato",
                ),
                recommendation=normalize_text(
                    row.get("recommendation"),
                    "Verificare e mitigare il finding.",
                ),
            )

            db.add(finding)
            created += 1

        except Exception as exc:
            errors.append(
                f"CyberFindings riga {index + 2}: {str(exc)}"
            )

    return {
        "processed": len(df),
        "created": created,
        "errors": errors,
    }


def import_threats(
    db: Session,
    company_id: int,
    df: pd.DataFrame,
) -> dict:
    df = normalize_dataframe(df)

    created = 0
    errors: list[str] = []

    for index, row in df.iterrows():
        try:
            title = normalize_text(row.get("title"))

            if not title:
                errors.append(
                    f"Threats riga {index + 2}: titolo mancante"
                )
                continue

            threat = CyberThreat(
                company_id=company_id,
                source=normalize_text(
                    row.get("source"),
                    "Import Enterprise",
                ),
                threat_type=normalize_text(
                    row.get("threat_type"),
                    "osint",
                ),
                title=title,
                description=normalize_text(
                    row.get("description"),
                    "Threat importata",
                ),
                cve_id=normalize_text(row.get("cve_id")),
                severity=normalize_text(
                    row.get("severity"),
                    "medium",
                ).lower(),
                score=normalize_float(
                    row.get("score"),
                    50,
                ),
            )

            db.add(threat)
            created += 1

        except Exception as exc:
            errors.append(
                f"Threats riga {index + 2}: {str(exc)}"
            )

    return {
        "processed": len(df),
        "created": created,
        "errors": errors,
    }


def import_optional_predictive(
    db: Session,
    company_id: int,
    df: pd.DataFrame,
) -> dict:
    try:
        from predictive_models import PredictiveInsight
    except ImportError:
        return {
            "processed": len(df),
            "created": 0,
            "skipped": True,
            "message": "Modello PredictiveInsight non disponibile",
            "errors": [],
        }

    df = normalize_dataframe(df)
    created = 0
    errors: list[str] = []

    for index, row in df.iterrows():
        try:
            insight = PredictiveInsight(
                company_id=company_id,
                finance_risk=normalize_float(
                    row.get("finance_risk"),
                    50,
                ),
                customer_risk=normalize_float(
                    row.get("customer_risk"),
                    50,
                ),
                compliance_risk=normalize_float(
                    row.get("compliance_risk"),
                    50,
                ),
                cyber_risk=normalize_float(
                    row.get("cyber_risk"),
                    50,
                ),
                prediction_score=normalize_float(
                    row.get("prediction_score"),
                    50,
                ),
                level=normalize_text(
                    row.get("level"),
                    "STABILE",
                ),
                summary="Import Enterprise Predictive",
                recommendation=normalize_text(
                    row.get("recommendation"),
                    "Continuare il monitoraggio.",
                ),
            )

            db.add(insight)
            created += 1

        except Exception as exc:
            errors.append(
                f"PredictiveHistory riga {index + 2}: {str(exc)}"
            )

    return {
        "processed": len(df),
        "created": created,
        "errors": errors,
    }


def import_optional_agents(
    db: Session,
    company_id: int,
    df: pd.DataFrame,
) -> dict:
    try:
        from agents_models import AgentRun
    except ImportError:
        return {
            "processed": len(df),
            "created": 0,
            "skipped": True,
            "message": "Modello AgentRun non disponibile",
            "errors": [],
        }

    df = normalize_dataframe(df)
    created = 0
    errors: list[str] = []

    for index, row in df.iterrows():
        try:
            run = AgentRun(
                company_id=company_id,
                agent_name=normalize_text(
                    row.get("agent_name"),
                    "Enterprise Agent",
                ),
                status=normalize_text(
                    row.get("status"),
                    "completed",
                ),
                summary=normalize_text(
                    row.get("summary"),
                    "Import Enterprise Agents",
                ),
                actions=normalize_text(
                    row.get("actions"),
                    "Verificare le azioni consigliate.",
                ),
                priority=normalize_text(
                    row.get("priority"),
                    "medium",
                ).lower(),
            )

            db.add(run)
            created += 1

        except Exception as exc:
            errors.append(
                f"AgentsHistory riga {index + 2}: {str(exc)}"
            )

    return {
        "processed": len(df),
        "created": created,
        "errors": errors,
    }


def import_enterprise_workbook(
    db: Session,
    company_id: int,
    file_path: str,
    filename: str,
) -> dict:
    if not filename.lower().endswith((".xlsx", ".xls")):
        raise ValueError(
            "Import Enterprise supporta file Excel .xlsx o .xls"
        )

    sheets: dict[str, pd.DataFrame] = pd.read_excel(
        file_path,
        sheet_name=None,
    )

    normalized_sheets = {
        normalize_column(sheet_name): dataframe
        for sheet_name, dataframe in sheets.items()
    }

    handlers = [
        ("customers", "Customers", import_customers),
        ("revenues", "Revenues", import_revenues),
        ("compliance", "Compliance", import_compliance),
        ("cyberassets", "CyberAssets", import_cyber_assets),
        ("cyberfindings", "CyberFindings", import_cyber_findings),
        ("threats", "Threats", import_threats),
        (
            "predictivehistory",
            "PredictiveHistory",
            import_optional_predictive,
        ),
        (
            "agentshistory",
            "AgentsHistory",
            import_optional_agents,
        ),
    ]

    result: dict[str, Any] = {
        "file_name": filename,
        "company_id": company_id,
        "available_sheets": list(sheets.keys()),
        "modules": {},
        "total_processed": 0,
        "total_created": 0,
        "total_updated": 0,
        "total_errors": 0,
    }

    for sheet_key, display_name, handler in handlers:
        dataframe = normalized_sheets.get(sheet_key)

        if dataframe is None:
            result["modules"][display_name] = {
                "processed": 0,
                "created": 0,
                "skipped": True,
                "message": "Foglio non presente",
                "errors": [],
            }
            continue

        module_result = handler(
            db=db,
            company_id=company_id,
            df=dataframe,
        )

        result["modules"][display_name] = module_result
        result["total_processed"] += module_result.get(
            "processed",
            0,
        )
        result["total_created"] += module_result.get(
            "created",
            0,
        )
        result["total_updated"] += module_result.get(
            "updated",
            0,
        )
        result["total_errors"] += len(
            module_result.get("errors", [])
        )

    job = ImportJob(
        company_id=company_id,
        file_name=filename,
        import_type="enterprise_workbook",
        status=(
            "completed"
            if result["total_errors"] == 0
            else "completed_with_errors"
        ),
        rows_processed=result["total_processed"],
        rows_created=result["total_created"],
        errors="\n".join(
            error
            for module in result["modules"].values()
            for error in module.get("errors", [])
        ),
    )

    db.add(job)
    db.commit()

    return result
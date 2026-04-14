import csv
import io
from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import or_
from sqlalchemy.orm import Session

from ..auth_utils import get_current_user
from ..database import get_db
from ..models import MaintenancePayment, User
from ..schemas import MaintenanceCreate, MaintenanceOut

router = APIRouter(prefix="/maintenance", tags=["maintenance"])


def _mark_overdue(records: list[MaintenancePayment]) -> None:
    today = date.today()
    for row in records:
        if row.status == "Pending" and row.due_date < today:
            row.status = "Overdue"


@router.get("", response_model=list[MaintenanceOut])
def list_maintenance(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role == "admin":
        rows = db.query(MaintenancePayment).order_by(MaintenancePayment.month.desc(), MaintenancePayment.flat_number.asc()).all()
    else:
        rows = (
            db.query(MaintenancePayment)
            .filter(MaintenancePayment.flat_number == current_user.flat_number)
            .order_by(MaintenancePayment.month.desc())
            .all()
        )
    _mark_overdue(rows)
    db.commit()
    return rows


@router.post("", response_model=MaintenanceOut)
def upsert_maintenance(payload: MaintenanceCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    row = (
        db.query(MaintenancePayment)
        .filter(MaintenancePayment.flat_number == payload.flat_number, MaintenancePayment.month == payload.month)
        .first()
    )
    if not row:
        row = MaintenancePayment(
            flat_number=payload.flat_number,
            month=payload.month,
            amount=payload.amount,
            due_date=payload.due_date,
            status=payload.status,
            paid_on=payload.paid_on,
            recorded_by=current_user.id,
        )
        db.add(row)
    else:
        row.amount = payload.amount
        row.due_date = payload.due_date
        row.status = payload.status
        row.paid_on = payload.paid_on
    db.commit()
    db.refresh(row)
    return row


@router.get("/export")
def export_csv(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    rows = db.query(MaintenancePayment).order_by(MaintenancePayment.month.desc()).all()
    stream = io.StringIO()
    writer = csv.writer(stream)
    writer.writerow(["flat_number", "month", "amount", "due_date", "status", "paid_on"])
    for row in rows:
        writer.writerow([row.flat_number, row.month, row.amount, row.due_date, row.status, row.paid_on])
    stream.seek(0)
    return StreamingResponse(
        iter([stream.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=maintenance.csv"},
    )


@router.get("/summary")
def summary(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    rows = db.query(MaintenancePayment).all()
    _mark_overdue(rows)
    db.commit()
    total = sum(r.amount for r in rows)
    paid = sum(r.amount for r in rows if r.status == "Paid")
    return {"total_amount": total, "paid_amount": paid, "progress_percent": round((paid / total * 100), 2) if total else 0}

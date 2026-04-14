import csv
import io

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from ..auth_utils import get_current_user
from ..database import get_db
from ..models import User
from ..schemas import ResidentProfileUpdate, UserOut

router = APIRouter(prefix="/residents", tags=["residents"])


@router.get("", response_model=list[UserOut])
def list_residents(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(User).order_by(User.flat_number.asc()).all()


@router.put("/me", response_model=UserOut)
def update_profile(payload: ResidentProfileUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    email_owner = db.query(User).filter(User.email == payload.email, User.id != current_user.id).first()
    if email_owner:
        raise HTTPException(status_code=400, detail="Email already in use")
    current_user.name = payload.name
    current_user.phone = payload.phone
    current_user.email = payload.email
    current_user.members_count = payload.members_count
    current_user.vehicle_numbers = payload.vehicle_numbers
    db.commit()
    db.refresh(current_user)
    return current_user


@router.get("/export")
def export_residents(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    rows = db.query(User).order_by(User.flat_number.asc()).all()
    stream = io.StringIO()
    writer = csv.writer(stream)
    writer.writerow(["flat_number", "name", "email", "phone", "members_count", "vehicle_numbers", "role"])
    for row in rows:
        writer.writerow([row.flat_number, row.name, row.email, row.phone, row.members_count, row.vehicle_numbers, row.role])
    stream.seek(0)
    return StreamingResponse(
        iter([stream.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=residents.csv"},
    )

import os
import shutil
from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from ..auth_utils import get_current_user
from ..database import get_db
from ..models import Complaint, User
from ..schemas import ComplaintOut, ComplaintUpdate

router = APIRouter(prefix="/complaints", tags=["complaints"])
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./data/uploads")


@router.get("", response_model=list[ComplaintOut])
def list_complaints(
    status: str | None = None,
    category: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Complaint)
    if current_user.role != "admin":
        query = query.filter(Complaint.user_id == current_user.id)
    if status:
        query = query.filter(Complaint.status == status)
    if category:
        query = query.filter(Complaint.category == category)
    return query.order_by(Complaint.created_at.desc()).all()


@router.post("", response_model=ComplaintOut)
def create_complaint(
    category: str = Form(...),
    subject: str = Form(...),
    description: str = Form(...),
    priority: str = Form(...),
    photo: UploadFile | None = File(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    photo_path = None
    if photo and photo.filename:
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        ext = os.path.splitext(photo.filename)[-1]
        filename = f"complaint_{uuid4().hex}{ext}"
        full_path = os.path.join(UPLOAD_DIR, filename)
        with open(full_path, "wb") as out_file:
            shutil.copyfileobj(photo.file, out_file)
        photo_path = f"/uploads/{filename}"

    complaint = Complaint(
        user_id=current_user.id,
        flat_number=current_user.flat_number,
        resident_name=current_user.name,
        category=category,
        subject=subject,
        description=description,
        priority=priority,
        photo_path=photo_path,
        created_at=datetime.utcnow(),
    )
    db.add(complaint)
    db.commit()
    db.refresh(complaint)
    return complaint


@router.put("/{complaint_id}", response_model=ComplaintOut)
def update_complaint(
    complaint_id: int,
    payload: ComplaintUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    complaint = db.get(Complaint, complaint_id)
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    complaint.status = payload.status
    complaint.assigned_to = payload.assigned_to
    complaint.resolution_notes = payload.resolution_notes
    db.commit()
    db.refresh(complaint)
    return complaint

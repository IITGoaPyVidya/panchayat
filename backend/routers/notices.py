import os
import shutil
from datetime import date
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from ..auth_utils import get_current_user
from ..database import get_db
from ..models import Notice, User
from ..schemas import NoticeOut

router = APIRouter(prefix="/notices", tags=["notices"])
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./data/uploads")


@router.get("", response_model=list[NoticeOut])
def list_notices(include_expired: bool = False, db: Session = Depends(get_db)):
    query = db.query(Notice)
    if not include_expired:
        query = query.filter((Notice.expires_on.is_(None)) | (Notice.expires_on >= date.today()))
    return query.order_by(Notice.is_pinned.desc(), Notice.created_at.desc()).all()


@router.post("", response_model=NoticeOut)
def create_notice(
    title: str = Form(...),
    content: str = Form(...),
    is_pinned: bool = Form(False),
    expires_on: str | None = Form(None),
    image: UploadFile | None = File(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    image_path = None
    if image and image.filename:
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        ext = os.path.splitext(image.filename)[-1]
        filename = f"notice_{uuid4().hex}{ext}"
        full_path = os.path.join(UPLOAD_DIR, filename)
        with open(full_path, "wb") as out_file:
            shutil.copyfileobj(image.file, out_file)
        image_path = f"/uploads/{filename}"

    notice = Notice(
        title=title,
        content=content,
        image_path=image_path,
        is_pinned=is_pinned,
        expires_on=date.fromisoformat(expires_on) if expires_on else None,
        created_by=current_user.id,
    )
    db.add(notice)
    db.commit()
    db.refresh(notice)
    return notice


@router.delete("/{notice_id}")
def delete_notice(notice_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    notice = db.get(Notice, notice_id)
    if not notice:
        raise HTTPException(status_code=404, detail="Notice not found")
    db.delete(notice)
    db.commit()
    return {"message": "Deleted"}

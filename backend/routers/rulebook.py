import os
import shutil
from datetime import datetime
from uuid import uuid4

import fitz
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from ..auth_utils import get_current_user
from ..database import get_db
from ..models import Rulebook, User

router = APIRouter(prefix="/rulebook", tags=["rulebook"])
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./data/uploads")


@router.get("")
def get_rulebook(db: Session = Depends(get_db)):
    rb = db.query(Rulebook).order_by(Rulebook.updated_at.desc()).first()
    if not rb:
        return None
    return {
        "id": rb.id,
        "title": rb.title,
        "file_path": rb.file_path,
        "key_rules_text": rb.key_rules_text,
        "updated_at": rb.updated_at,
    }


@router.post("")
def upload_rulebook(
    title: str = Form("Society Rulebook"),
    key_rules_text: str = Form(""),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF allowed")

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    filename = f"rulebook_{uuid4().hex}.pdf"
    save_path = os.path.join(UPLOAD_DIR, filename)
    with open(save_path, "wb") as out_file:
        shutil.copyfileobj(file.file, out_file)

    rulebook = Rulebook(
        title=title,
        file_path=f"/uploads/{filename}",
        key_rules_text=key_rules_text,
        uploaded_by=current_user.id,
        updated_at=datetime.utcnow(),
    )
    db.add(rulebook)
    db.commit()
    db.refresh(rulebook)
    return {"message": "Uploaded", "id": rulebook.id}


@router.get("/search")
def search_rulebook(q: str, db: Session = Depends(get_db)):
    rb = db.query(Rulebook).order_by(Rulebook.updated_at.desc()).first()
    if not rb:
        return {"matches": []}
    path = rb.file_path.replace("/uploads/", "")
    full_path = os.path.join(UPLOAD_DIR, path)
    if not os.path.exists(full_path):
        return {"matches": []}

    doc = fitz.open(full_path)
    matches: list[dict] = []
    for idx, page in enumerate(doc):
        text = page.get_text("text")
        if q.lower() in text.lower():
            snippet = text[:500]
            matches.append({"page": idx + 1, "snippet": snippet})
    return {"matches": matches}

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..auth_utils import get_current_user
from ..database import get_db
from ..models import Contact, User
from ..schemas import ContactCreate, ContactOut, ContactUpdate

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.get("", response_model=list[ContactOut])
def list_contacts(db: Session = Depends(get_db)):
    return db.query(Contact).order_by(Contact.category.asc(), Contact.name.asc()).all()


@router.post("", response_model=ContactOut)
def create_contact(payload: ContactCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    contact = Contact(
        name=payload.name,
        category=payload.category,
        phone=payload.phone,
        owner_id=current_user.id,
        added_by_flat=current_user.flat_number,
    )
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


def _check_can_edit(contact: Contact, user: User):
    if user.role != "admin" and contact.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Not allowed")


@router.put("/{contact_id}", response_model=ContactOut)
def update_contact(contact_id: int, payload: ContactUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    contact = db.get(Contact, contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    _check_can_edit(contact, current_user)
    contact.name = payload.name
    contact.category = payload.category
    contact.phone = payload.phone
    db.commit()
    db.refresh(contact)
    return contact


@router.delete("/{contact_id}")
def delete_contact(contact_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    contact = db.get(Contact, contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    _check_can_edit(contact, current_user)
    db.delete(contact)
    db.commit()
    return {"message": "Deleted"}

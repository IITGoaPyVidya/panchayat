from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..auth_utils import create_access_token, get_current_user, hash_password, verify_password
from ..database import get_db
from ..models import User
from ..schemas import Token, UserLogin, UserOut, UserSignup

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=UserOut)
def signup(payload: UserSignup, db: Session = Depends(get_db)):
    existing = db.query(User).filter((User.email == payload.email) | (User.flat_number == payload.flat_number)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email or flat number already exists")
    user = User(
        name=payload.name,
        email=payload.email,
        phone=payload.phone,
        hashed_password=hash_password(payload.password),
        flat_number=payload.flat_number,
        role=payload.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=Token)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": str(user.id), "role": user.role})
    return Token(access_token=token)


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return current_user

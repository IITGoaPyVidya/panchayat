from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..auth_utils import create_access_token, get_current_user, hash_password, verify_password
from ..database import get_db
from ..models import User
from ..schemas import Token, UserLogin, UserOut, UserSignup

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=UserOut)
def signup(payload: UserSignup, db: Session = Depends(get_db)):
    print(f"DEBUG SIGNUP: Received signup for email: {payload.email}")
    existing = db.query(User).filter((User.email == payload.email) | (User.flat_number == payload.flat_number)).first()
    if existing:
        print(f"DEBUG SIGNUP: User already exists")
        raise HTTPException(status_code=400, detail="Email or flat number already exists")
    
    hashed_pwd = hash_password(payload.password)
    print(f"DEBUG SIGNUP: Hashed password: {hashed_pwd}")
    
    user = User(
        name=payload.name,
        email=payload.email,
        phone=payload.phone,
        hashed_password=hashed_pwd,
        flat_number=payload.flat_number,
        role=payload.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    print(f"DEBUG SIGNUP: User created successfully with email: {user.email}")
    return user


@router.post("/login", response_model=Token)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        print(f"DEBUG: No user found with email {payload.email}")
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    print(f"DEBUG: User found: {user.email}")
    print(f"DEBUG: Password provided: {payload.password}")
    print(f"DEBUG: Hashed password in DB: {user.hashed_password}")
    
    password_valid = verify_password(payload.password, user.hashed_password)
    print(f"DEBUG: Password valid: {password_valid}")
    
    if not password_valid:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_access_token({"sub": str(user.id), "role": user.role})
    return Token(access_token=token)


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return current_user

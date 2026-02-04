from fastapi import APIRouter, Depends, HTTPException, status
from schema.user import Token, UserCreate, UserLogin
from sqlalchemy.orm import Session
from db.db import get_db
from models.user import User
from utilities.crypt import get_password_hash, create_access_token
from utilities.auth import authenticate_user, get_current_user, require_role
from datetime import timedelta

router = APIRouter()

@router.post("/register", response_model=Token)
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter((User.username == user.username) | (User.email == user.email)).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username or email already registered")
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        role=user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": db_user.username, "role": db_user.role}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
async def login_user(user: UserLogin, db: Session = Depends(get_db)):
    db_user = authenticate_user(db, user.username, user.password)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": db_user.username, "role": db_user.role}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Protected endpoint to get current user info
@router.get("/me")
async def read_users_me(current_user = Depends(get_current_user)):
    return {"username": current_user.username, "role": current_user.role}

# Example of role-based access control
@router.get("/admin-only")
async def admin_endpoint(current_user = Depends(require_role("admin"))):
    return {"message": "This is admin only"}
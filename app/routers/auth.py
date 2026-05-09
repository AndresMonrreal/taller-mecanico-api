from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.models.users import User
from app.schemas.users import UserCreate, UserLogin, UserOut, Token
from app.auth.jwt import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserOut)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    existente = db.query(User).filter(User.usr_username == user_in.usr_username).first()
    if existente:
        raise HTTPException(status_code=400, detail="Usuario ya existe")
    usuario = User(
        usr_username=user_in.usr_username,
        usr_password=hash_password(user_in.usr_password),
        usr_rol=user_in.usr_rol
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario

@router.post("/login", response_model=Token)
def login(user_in: UserLogin, db: Session = Depends(get_db)):
    usuario = db.query(User).filter(User.usr_username == user_in.usr_username).first()
    if not usuario or not verify_password(user_in.usr_password, usuario.usr_password):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    token = create_access_token({"sub": usuario.usr_username, "rol": usuario.usr_rol})
    return {"access_token": token, "token_type": "bearer", "rol": usuario.usr_rol}
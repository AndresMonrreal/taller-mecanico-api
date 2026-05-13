from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.models.users import User
from app.models.permiso_rol import PermisoRol
from app.schemas.users import UserCreate, UserLogin, UserOut, Token, PermisoRolOut
from app.auth.jwt import hash_password, verify_password, create_access_token
from typing import List

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

@router.get("/roles", response_model=List[PermisoRolOut])
def get_roles(db: Session = Depends(get_db)):
    return db.query(PermisoRol).all()

@router.get("/permisos/{rol}", response_model=PermisoRolOut)
def get_permiso_rol(rol: str, db: Session = Depends(get_db)):
    permiso = db.query(PermisoRol).filter(PermisoRol.rol_nombre == rol).first()
    if not permiso:
        raise HTTPException(status_code=404, detail="Rol no encontrado")
    return permiso
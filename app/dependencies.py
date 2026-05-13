from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.auth.jwt import decode_token
from app.models.users import User
from app.auth.permissions import tiene_permiso_bd

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Token inválido")
    user = db.query(User).filter(User.usr_username == payload.get("sub")).first()
    if not user:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")
    return user

def require_permiso(permiso: int):
    def checker(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
        if not tiene_permiso_bd(db, current_user.usr_rol, permiso):
            raise HTTPException(status_code=403, detail="Sin permisos suficientes")
        return current_user
    return checker
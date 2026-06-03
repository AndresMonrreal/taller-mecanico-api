from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.db import get_db
from app.auth.jwt import decode_token
from app.models.users import User
from app.auth.permissions import tiene_permiso_bd

# Esquema OAuth2 que extrae el token del header Authorization: Bearer <token>
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Token inválido")
    
    user = db.query(User).filter(User.usr_username == payload.get("sub")).first()
    if not user:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")
    
    ses_id = payload.get("ses_id")
    user.ses_id = ses_id
    
    # Establece CLIENT_IDENTIFIER en Oracle para que los triggers
    # de ses_id tomen el valor correcto via SYS_CONTEXT('USERENV','CLIENT_IDENTIFIER')
    db.execute(
        text("BEGIN DBMS_SESSION.SET_IDENTIFIER(:sid); END;"),
        {"sid": str(ses_id)}
    )
    
    return user


def require_permiso(permiso: int):
    """
    Fábrica de dependencias que verifica que el usuario tenga un permiso específico.
    Se usa como: Depends(require_permiso(PERM_EDITAR))
    
    Args:
        permiso: Máscara del permiso requerido (ej: PERM_EDITAR)
    
    Returns:
        Función checker que valida el permiso del usuario autenticado
        Con ses_id adjunto para usarlo en endpoints protegidos
    
    Raises:
        HTTPException 403: Si el usuario no tiene el permiso requerido
    """
    def checker(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
        if not tiene_permiso_bd(db, current_user.usr_rol, permiso):
            raise HTTPException(status_code=403, detail="Sin permisos suficientes")
        return current_user
    return checker
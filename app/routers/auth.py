from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.models.users import User
from app.models.sesion import Session as SessionModel
from app.models.permiso_rol import PermisoRol
from app.schemas.users import UserCreate, UserLogin, UserOut, Token, PermisoRolOut
from app.auth.jwt import hash_password, verify_password, create_access_token
from typing import List

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserOut)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    """Registra un nuevo usuario en el sistema. Valida que el username no exista."""
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
    """Autentica un usuario, crea sesión en BD y retorna token JWT con ses_id."""
    usuario = db.query(User).filter(User.usr_username == user_in.usr_username).first()
    if not usuario or not verify_password(user_in.usr_password, usuario.usr_password):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")

    # Crear registro en Sessions
    nueva_sesion = SessionModel(ses_usuario=usuario.usr_username)
    db.add(nueva_sesion)
    db.commit()
    db.refresh(nueva_sesion)

    # Meter ses_id en el token
    token = create_access_token({
        "sub": usuario.usr_username,
        "rol": usuario.usr_rol,
        "ses_id": nueva_sesion.ses_id
    })

    return {
        "access_token": token,
        "token_type": "bearer",
        "rol": usuario.usr_rol,
        "usr_username": usuario.usr_username
    }


@router.get("/roles", response_model=List[PermisoRolOut])
def get_roles(db: Session = Depends(get_db)):
    """Retorna la lista de todos los roles definidos en el sistema."""
    return db.query(PermisoRol).all()


@router.get("/permisos/{rol}", response_model=PermisoRolOut)
def get_permiso_rol(rol: str, db: Session = Depends(get_db)):
    """Retorna el bitmask de permisos para un rol específico."""
    permiso = db.query(PermisoRol).filter(PermisoRol.rol_nombre == rol).first()
    if not permiso:
        raise HTTPException(status_code=404, detail="Rol no encontrado")
    return permiso
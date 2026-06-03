from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.crud.cliente import crud_client
from app.schemas.cliente import ClientCreate, ClientUpdate, ClientOut
from app.dependencies import get_current_user
from app.models.users import User
from typing import List
from sqlalchemy import text


router = APIRouter(prefix="/clients", tags=["Clients"])


@router.get("/", response_model=List[ClientOut])
def get_clients(skip: int = 0, limit: int = 10, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Retorna lista paginada de todos los clientes. Requiere autenticación."""
    return crud_client.get_all(db, skip=skip, limit=limit)


@router.get("/vista/resumen")
def get_resumen_clientes(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Retorna vista resumen de clientes desde la base de datos Oracle (vw_resumen_clientes)."""
    result = db.execute(text("SELECT * FROM vw_resumen_clientes")).mappings().all()
    return [dict(r) for r in result]


@router.get("/{cli_id}", response_model=ClientOut)
def get_client(cli_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Retorna un cliente específico por su ID."""
    client = crud_client.get(db, cli_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client


@router.post("/", response_model=ClientOut)
def create_client(client_in: ClientCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Crea un nuevo cliente. Valida que el email no esté registrado previamente."""
    existing_client = crud_client.get_by_email(db, client_in.cli_email)
    if existing_client:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud_client.create(db, client_in.model_dump())


@router.patch("/{cli_id}", response_model=ClientOut)
def update_client(cli_id: int, client_in: ClientUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Actualiza los datos de un cliente existente."""
    client = crud_client.get(db, cli_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return crud_client.update(db, client, client_in.model_dump())


@router.delete("/{cli_id}")
def delete_client(cli_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Elimina un cliente y sus vehículos asociados (delete-orphan)."""
    client = crud_client.delete(db, cli_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return {"message": f"Client {cli_id} deleted"}

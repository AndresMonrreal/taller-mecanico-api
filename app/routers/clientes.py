from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.crud.cliente import crud_client
from app.schemas.cliente import ClientCreate, ClientUpdate, ClientOut
from typing import List

router = APIRouter(prefix = "/clients", tags = ["Clients"])

@router.get("/", response_model=List[ClientOut])
def get_clients(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud_client.get_all(db, skip=skip, limit=limit)

@router.get("/{cli_id}",response_model = ClientOut)
def get_client(cli_id: int, db: Session = Depends(get_db)):
    client = crud_client.get(db, cli_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client

@router.post("/", response_model = ClientOut)
def create_client(client_in: ClientCreate, db: Session = Depends(get_db)):
    existing_client = crud_client.get_by_email(db, client_in.cli_email)
    if existing_client:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud_client.create(db, client_in.model_dump())

@router.patch("/{cli_id}", response_model = ClientOut)
def update_client(cli_id:int, client_in: ClientUpdate, db: Session = Depends(get_db)):
    client = crud_client.get(db, cli_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return crud_client.update(db, client, client_in.model_dump())


@router.delete("/{cli_id}")
def delete_client(cli_id: int, db: Session = Depends(get_db)):
    client = crud_client.get(db, cli_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return {"message" : f"Client with id {cli_id} deleted successfully"}
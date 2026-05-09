from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.crud.servicio import crud_Service
from app.schemas.servicio import ServiceCreate, ServiceOut, ServiceUpdate
from typing import List

router = APIRouter(prefix="/servicios", tags=["servicios"])

@router.get("/", response_model=List[ServiceOut])
def get_servicios(db: Session = Depends(get_db)):
    return crud_Service.get_all(db)

@router.get("/{srv_id}", response_model=ServiceOut)
def get_servicio(srv_id: int, db: Session = Depends(get_db)):
    servicio = crud_Service.get(db, srv_id)
    if not servicio:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")
    return servicio

@router.post("/", response_model=ServiceOut)
def create_servicio(servicio_in: ServiceCreate, db: Session = Depends(get_db)):
    existente = crud_Service.get_by_name(db, servicio_in.srv_name)
    if existente:
        raise HTTPException(status_code=400, detail="Servicio ya existe")
    return crud_Service.create(db, servicio_in.model_dump())

@router.patch("/{srv_id}", response_model=ServiceOut)
def update_servicio(srv_id: int, servicio_in: ServiceUpdate, db: Session = Depends(get_db)):
    servicio = crud_Service.get(db, srv_id)
    if not servicio:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")
    return crud_Service.update(db, servicio, servicio_in.model_dump())

@router.delete("/{srv_id}")
def delete_servicio(srv_id: int, db: Session = Depends(get_db)):
    servicio = crud_Service.delete(db, srv_id)
    if not servicio:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")
    return {"message": "Servicio eliminado"}
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.crud.vehiculo import crud_vehiculo
from app.schemas.vehiculo import VehicleCreate, VehicleUpdate, VehicleOut
from app.schemas.pagination import Pagination
from app.dependencies import get_current_user
from app.models.users import User
from typing import List

router = APIRouter(prefix="/vehiculos", tags=["vehiculos"])


@router.get("/", response_model=Pagination[VehicleOut])
def get_vehiculos(page: int = 1, page_size: int = 10, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Retorna vehículos paginados. Parámetros: page (default 1), page_size (default 10)."""
    return crud_vehiculo.get_pagination(db, page=page, size=page_size)


@router.get("/{veh_id}", response_model=VehicleOut)
def get_vehiculo(veh_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Retorna un vehículo específico por su ID."""
    vehiculo = crud_vehiculo.get(db, veh_id)
    if not vehiculo:
        raise HTTPException(status_code=404, detail="Vehiculo no encontrado")
    return vehiculo


@router.get("/cliente/{cli_id}", response_model=List[VehicleOut])
def get_vehiculos_by_cliente(cli_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Retorna todos los vehículos de un cliente específico."""
    return crud_vehiculo.get_by_client(db, cli_id)


@router.post("/", response_model=VehicleOut)
def create_vehiculo(vehiculo_in: VehicleCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Registra un nuevo vehículo. Valida que la placa no esté duplicada."""
    existente = crud_vehiculo.get_by_plate(db, vehiculo_in.veh_plate)
    if existente:
        raise HTTPException(status_code=400, detail="Placa ya registrada")
    return crud_vehiculo.create(db, vehiculo_in.model_dump())


@router.patch("/{veh_id}", response_model=VehicleOut)
def update_vehiculo(veh_id: int, vehiculo_in: VehicleUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Actualiza los datos de un vehículo existente."""
    vehiculo = crud_vehiculo.get(db, veh_id)
    if not vehiculo:
        raise HTTPException(status_code=404, detail="Vehiculo no encontrado")
    return crud_vehiculo.update(db, vehiculo, vehiculo_in.model_dump())


@router.delete("/{veh_id}")
def delete_vehiculo(veh_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Elimina un vehículo y sus órdenes asociadas (delete-orphan)."""
    vehiculo = crud_vehiculo.delete(db, veh_id)
    if not vehiculo:
        raise HTTPException(status_code=404, detail="Vehiculo no encontrado")
    return {"message": "Vehiculo eliminado"}
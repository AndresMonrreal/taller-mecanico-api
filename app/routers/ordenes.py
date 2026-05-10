from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.crud.orden import crud_orden
from app.schemas.orden import OrderCreate, OrderOut, OrderUpdate
from typing import List

router = APIRouter(prefix="/ordenes", tags=["ordenes"])

@router.get("/", response_model=List[OrderOut])
def get_ordenes(db: Session = Depends(get_db)):
    try:
        return crud_orden.get_all(db)
    except Exception as e:
        print(f"ERROR GET ORDENES: {e}")
        raise
    
@router.get("/{ord_id}", response_model=OrderOut)
def get_orden(ord_id: int, db: Session = Depends(get_db)):
    orden = crud_orden.get(db, ord_id)
    if not orden:
        raise HTTPException(status_code=404, detail="Orden no encontrada")
    return orden

@router.post("/", response_model=OrderOut)
def create_orden(orden_in: OrderCreate, db: Session = Depends(get_db)):
    data = orden_in.model_dump(exclude={"services"})
    servicios = [s.model_dump() for s in orden_in.services]
    return crud_orden.create_with_services(db, data, servicios)

@router.patch("/{ord_id}", response_model=OrderOut)
def update_orden(ord_id: int, orden_in: OrderUpdate, db: Session = Depends(get_db)):
    orden = crud_orden.get(db, ord_id)
    if not orden:
        raise HTTPException(status_code=404, detail="Orden no encontrada")
    return crud_orden.update(db, db_obj=orden, obj_in=orden_in.model_dump(exclude_unset=True))

@router.delete("/{ord_id}")
def delete_orden(ord_id: int, db: Session = Depends(get_db)):
    orden = crud_orden.delete(db, ord_id)
    if not orden:
        raise HTTPException(status_code=404, detail="Orden no encontrada")
    return {"message": "Orden eliminada"}
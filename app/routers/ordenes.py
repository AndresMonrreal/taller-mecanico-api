from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.crud.orden import crud_orden
from app.schemas.orden import OrderCreate, OrderOut, OrderUpdate
from app.dependencies import get_current_user
from app.models.users import User
from typing import List
from sqlalchemy import text


router = APIRouter(prefix="/ordenes", tags=["ordenes"])

@router.get("/", response_model=List[OrderOut])
def get_ordenes(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        return crud_orden.get_all(db)
    except Exception as e:
        print(f"ERROR GET ORDENES: {e}")
        raise
    

@router.get("/vista/activas")
def get_ordenes_activas_vista(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = db.execute(text("SELECT * FROM vw_ordenes_activas")).mappings().all()
    return [dict(r) for r in result]
    
@router.get("/{ord_id}", response_model=OrderOut)
def get_orden(ord_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    orden = crud_orden.get(db, ord_id)
    if not orden:
        raise HTTPException(status_code=404, detail="Orden no encontrada")
    return orden

@router.post("/", response_model=OrderOut)
def create_orden(orden_in: OrderCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    data = orden_in.model_dump(exclude={"services"})
    servicios = [s.model_dump() for s in orden_in.services]
    return crud_orden.create_with_services(db, data, servicios)

@router.patch("/{ord_id}", response_model=OrderOut)
def update_orden(ord_id: int, orden_in: OrderUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    orden = crud_orden.get(db, ord_id)
    if not orden:
        raise HTTPException(status_code=404, detail="Orden no encontrada")
    return crud_orden.update(db, db_obj=orden, obj_in=orden_in.model_dump(exclude_unset=True))

@router.delete("/{ord_id}")
def delete_orden(ord_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    orden = crud_orden.delete(db, ord_id)
    if not orden:
        raise HTTPException(status_code=404, detail="Orden no encontrada")
    return {"message": "Orden eliminada"}

@router.patch("/{ord_id}/cerrar")
def cerrar_orden(ord_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        conn = db.connection()
        cursor = conn.connection.cursor()
        mensaje = cursor.var(str)
        cursor.callproc("sp_cerrar_orden", [ord_id, mensaje])
        cursor.close()
        db.commit()
        result = mensaje.getvalue()
        return {"message": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{ord_id}/total")
def get_total_orden(ord_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = db.execute(
        text("SELECT fn_calcular_total_orden(:ord_id) FROM dual"),
        {"ord_id": ord_id}
    ).scalar()
    return {"ord_id": ord_id, "total": float(result or 0)}



from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.crud.orden import crud_orden
from app.schemas.orden import OrderCreate, OrderOut, OrderUpdate
from app.dependencies import get_current_user
from app.models.users import User
from typing import List
from sqlalchemy import text
from pydantic import BaseModel


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

@router.patch("/{ord_id}/calcular-totales")
def calcular_totales(ord_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        db.execute(text("""
            UPDATE "ServiceOrders" so
            SET ords_total = so.ords_hours * (
                SELECT srv_price_hour FROM "Service" WHERE srv_id = so.srv_id
            )
            WHERE so.ord_id = :ord_id
            AND so.ords_total IS NULL
        """), {"ord_id": ord_id})
        db.commit()
        return {"message": "Totales calculados"}
    except Exception as e:
        print(f"ERROR CALCULAR TOTALES: {e}")  # <-- esto
        raise HTTPException(status_code=500, detail=str(e))

class TransferirServicioIn(BaseModel):
    srv_ord_id: int
    ord_id_new: int
    
@router.post("/transferir-servicio")
def transferir_servicio(
    data: TransferirServicioIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
    ):
    try:
        conn = db.connection()
        cursor = conn.connection.cursor()
        mensaje = cursor.var(str)
        cursor.callproc("sp_transferir_servicio", [data.srv_ord_id, data.ord_id_new, mensaje])
        cursor.close()
        db.commit()
        return {"message": mensaje.getvalue()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{ord_id}/servicios")
def get_servicios_orden(ord_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = db.execute(
        text("""
            SELECT so.srv_ord_id, so.srv_id, so.ords_hours, so.ords_total,
                   s.srv_name, s.srv_price_hour
            FROM "ServiceOrders" so
            JOIN "Service" s ON so.srv_id = s.srv_id
            WHERE so.ord_id = :ord_id
        """),
        {"ord_id": ord_id}
    ).mappings().all()
    return [dict(r) for r in result]
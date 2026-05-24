from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.orden import Order
from app.models.orden_servicio import ServiceOrder
from app.models.servicio import Service
from decimal import Decimal

class CRUDOrden(CRUDBase[Order]):
    def get_by_vehicle(self, db: Session, veh_id: int):
        return db.query(Order).filter(Order.veh_id == veh_id).all()

    def get_by_status(self, db: Session, status: str):
        return db.query(Order).filter(Order.ord_status == status).all()

    def create_with_services(self, db: Session, order_data: dict, services: list):
        try:
            #Hcemos un savepoint para manejar la transacción
            db.begin_nested()
            #Creamos la orden con los datos proporcionados
            order = Order(**order_data)
            db.add(order)
            #Despues de insertar la orden, hacemos flush para obtener el ord_id generado
            db.flush()
            #insertamos los servicios asociados a la orden
            for srv in services:
                service = db.query(Service).filter(Service.srv_id == srv['srv_id']).first()
                if service:
                    total = Decimal(str(srv["ords_hours"])) * service.srv_price_hour
                    orden_srv = ServiceOrder(
                        ord_id=order.ord_id,
                        srv_id=srv['srv_id'],
                        ords_hours=srv["ords_hours"],
                        ords_total=total
                    )
                    db.add(orden_srv)
            
            db.commit()
            db.refresh(order)
            return order
        except Exception as e:
            db.rollback()
            raise e

    def delete(self, db: Session, id: int):
        orden = db.query(Order).filter(Order.ord_id == id).first()
        if orden:
            db.query(ServiceOrder).filter(ServiceOrder.ord_id == id).delete()
            db.delete(orden)
            db.commit()
        return orden

crud_orden = CRUDOrden(Order)
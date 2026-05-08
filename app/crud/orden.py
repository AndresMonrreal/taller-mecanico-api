from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.orden import Order
from app.models.orden_servicio import ServiceOrder
from app.models.servicio import Service
from decimal import Decimal

class CRUDOrden(CRUDBase[Order]):
    def get_by_vehicle(self,db:Session,veh_id:int):
        return db.query(Order).filter(Order.veh_id == veh_id).all()
    
    def get_by_status(self,db:Session,status:str):
        return db.query(Order).filter(Order.ord_status == status).all()
    
    
    def create_with_services(self,db:Session,order_data:dict,services:list):
        try:
            order = Order(**order_data)
            db.add(order)
            db.flush()  # Para obtener el ID de la orden antes de agregar los servicios
            
            for srv in services:
                service = db.query(service).get(srv['ser_id'])
                total = Decimal(str(srv["ords_hours"])) * service.srv_price
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
        
crud_orden = CRUDOrden(Order)   

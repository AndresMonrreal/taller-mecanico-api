from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.vehiculo import Vehicle

class CRUDOrden(CRUDBase[Vehicle]):
    def get_by_plate(self,db:Session,plate:str):
        return db.query(self.model).filter(Vehicle.veh_plate == plate).first()
    
    def get_by_client(self,db:Session,cli_id:int):
        return db.query(self.model).filter(Vehicle.cli_id == cli_id).all()
    
crud_vehiculo = CRUDOrden(Vehicle)
    
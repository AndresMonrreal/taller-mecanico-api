from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.servicio import Service

class CRUDService(CRUDBase[Service]):
    def get_by_name(self,db:Session,name:str):
        return db.query(self.model).filter(Service.ser_name == name).first()
    
    
crud_Service = CRUDService(Service)    
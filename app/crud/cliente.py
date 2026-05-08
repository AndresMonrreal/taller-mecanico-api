from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.cliente import Client

class CRUCDClient(CRUDBase[Client]):
    def get_by_email(self,db:Session,email:str):
        return db.query(self.model).filter(Client.cli_email == email).first()
    
    def get_by_phone(self,db:Session,phone:str):
        return db.query(self.model).filter(Client.cli_phone == phone).first()
    
crud_client = CRUCDClient(Client)    
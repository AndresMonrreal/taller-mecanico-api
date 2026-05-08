from sqlalchemy.orm import Session
from typing import Type, TypeVar, Generic ,Optional,List
from app.core.db import Base

ModelType = TypeVar("ModelType", bound=Base)

class CRUDBase(Generic[ModelType]):
    def __init__(self,model:Type[ModelType]):
        self.model = model
        
    def get(self,db:Session,id:int) -> Optional[ModelType]:
        return db.query(self.model).filter(self.model.id == id).first()
    
    def get_all(self,db:Session, skip: int = 0, limit:int = 100) -> List[ModelType]:
        return db.query(self.model).offset(skip).limit(limit).all()
    
    def create(self,db:Session,obj_in:dict) -> ModelType:
        db_obj = self.model(**obj_in)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj        
    
    def update(self,db:Session,db_obj:ModelType,obj_in:dict) -> ModelType:
        for field, value in obj_in.items():
            if value is not None:
                setattr(db_obj, field, value)
                
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def delete(self,db:Session,id: int) -> ModelType:
        obj = db.query(self.model).filter(self.model.id == id).first()
        if obj:
            db.delete(obj)
            db.commit()
        return obj
from sqlalchemy.orm import Session
from typing import Type, TypeVar, Generic ,Optional,List
from app.core.db import Base

ModelType = TypeVar("ModelType", bound=Base)

class CRUDBase(Generic[ModelType]):
    def __init__(self,model:Type[ModelType]):
        self.model = model
        
    def get_pagination(self,db:Session,page:int = 1, size:int = 10):
        total = db.query(self.model).count()
        data = db.query(self.model).offset((page - 1) * size).limit(size).all()
        return {
            "total": total,
            "page": page,
            "size": size,
            "pages": ( total + size - 1) // size,
            "data": data
        }    
        
    def get(self, db: Session, id: int) -> Optional[ModelType]:
        pk_col_name = list(self.model.__table__.primary_key)[0].name
        return db.query(self.model).filter(
            getattr(self.model, pk_col_name) == id
        ).first()  
    
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
    
    def delete(self, db: Session, id: int) -> Optional[ModelType]:
        pk_col_name = list(self.model.__table__.primary_key)[0].name
        print(f"Buscando {self.model.__tablename__} con {pk_col_name} = {id}")
        obj = db.query(self.model).filter(
            getattr(self.model, pk_col_name) == id
        ).first()
        print(f"Encontrado: {obj}")
        if obj:
            db.delete(obj)
            db.commit()
            print("Eliminado y commiteado")
        return obj
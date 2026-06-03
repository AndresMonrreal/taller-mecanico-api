from sqlalchemy.orm import Session
from typing import Type, TypeVar, Generic, Optional, List
from app.core.db import Base

# Tipo genérico vinculado a la clase Base de SQLAlchemy
ModelType = TypeVar("ModelType", bound=Base)


class CRUDBase(Generic[ModelType]):
    """
    Clase base genérica para operaciones CRUD sobre cualquier modelo SQLAlchemy.
    Proporciona implementaciones por defecto de crear, leer, actualizar y eliminar.
    """

    def __init__(self, model: Type[ModelType]):
        """Inicializa el CRUD con el modelo SQLAlchemy asociado."""
        self.model = model

    def get_pagination(self, db: Session, page: int = 1, size: int = 10):
        """
        Retorna una lista paginada de registros con metadatos.

        Args:
            db: Sesión de base de datos
            page: Número de página actual
            size: Cantidad de registros por página

        Returns:
            Dict con total, page, size, pages y data
        """
        total = db.query(self.model).count()
        data = db.query(self.model).offset((page - 1) * size).limit(size).all()
        return {
            "total": total,
            "page": page,
            "size": size,
            "pages": (total + size - 1) // size,
            "data": data
        }

    def get(self, db: Session, id: int) -> Optional[ModelType]:
        """
        Obtiene un registro por su ID (columna primary key).

        Args:
            db: Sesión de base de datos
            id: Valor del primary key

        Returns:
            Objeto del modelo o None si no existe
        """
        pk_col_name = list(self.model.__table__.primary_key)[0].name
        return db.query(self.model).filter(
            getattr(self.model, pk_col_name) == id
        ).first()

    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """
        Obtiene todos los registros con paginación básica (skip/limit).

        Args:
            db: Sesión de base de datos
            skip: Registros a saltar
            limit: Máximo de registros a retornar

        Returns:
            Lista de objetos del modelo
        """
        return db.query(self.model).offset(skip).limit(limit).all()

    def create(self, db: Session, obj_in: dict) -> ModelType:
        """
        Crea un nuevo registro en la base de datos.

        Args:
            db: Sesión de base de datos
            obj_in: Diccionario con los datos del nuevo registro

        Returns:
            Objeto del modelo recién creado
        """
        obj_in.pop("ses_id", None)
        db_obj = self.model(**obj_in)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, db_obj: ModelType, obj_in: dict) -> ModelType:
        """
        Actualiza un registro existente. Solo modifica los campos con valor no nulo.

        Args:
            db: Sesión de base de datos
            db_obj: Objeto existente a actualizar
            obj_in: Diccionario con los campos a modificar

        Returns:
            Objeto actualizado
        """
        obj_in.pop("ses_id", None)
        for field, value in obj_in.items():
            if value is not None:
                setattr(db_obj, field, value)

        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, id: int) -> Optional[ModelType]:
        """
        Elimina un registro por su ID.

        Args:
            db: Sesión de base de datos
            id: Valor del primary key del registro a eliminar

        Returns:
            Objeto eliminado o None si no existe
        """
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
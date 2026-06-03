from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.servicio import Service


class CRUDService(CRUDBase[Service]):
    """
    CRUD especializado para el modelo Service.
    Agrega búsqueda de servicios por nombre.
    """

    def get_by_name(self, db: Session, name: str):
        """Busca un servicio por su nombre exacto."""
        return db.query(self.model).filter(Service.srv_name == name).first()


crud_Service = CRUDService(Service)
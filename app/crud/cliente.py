from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.cliente import Client


class CRUCDClient(CRUDBase[Client]):
    """
    CRUD especializado para el modelo Client.
    Agrega métodos de búsqueda por email y teléfono.
    """

    def get_by_email(self, db: Session, email: str):
        """Busca un cliente por su correo electrónico."""
        return db.query(self.model).filter(Client.cli_email == email).first()

    def get_by_phone(self, db: Session, phone: str):
        """Busca un cliente por su número de teléfono."""
        return db.query(self.model).filter(Client.cli_phone == phone).first()


crud_client = CRUCDClient(Client)
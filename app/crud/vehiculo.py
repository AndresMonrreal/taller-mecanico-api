from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.vehiculo import Vehicle


class CRUDVehicle(CRUDBase[Vehicle]):
    """
    CRUD especializado para el modelo Vehicle.
    Agrega búsqueda por placa y por cliente propietario.
    """

    def get_by_plate(self, db: Session, plate: str):
        """Busca un vehículo por su número de placa/matrícula."""
        return db.query(self.model).filter(Vehicle.veh_plate == plate).first()

    def get_by_client(self, db: Session, cli_id: int):
        """Obtiene todos los vehículos de un cliente específico."""
        return db.query(self.model).filter(Vehicle.cli_id == cli_id).all()


crud_vehiculo = CRUDVehicle(Vehicle)
    
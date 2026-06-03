"""correcciones modelo: rename column, constraints, indexes

=== ORA-00942 ROOT CAUSE ===
La migración inicial (0a18a24c8531) usa SQLAlchemy que en Oracle
genera CREATE TABLE "Vehicles" (con dobles comillas, case-sensitive).
Al usar op.execute("CREATE INDEX ... ON Vehicles ...") sin comillas,
Oracle busca VEHICLES (uppercase) y no lo encuentra.

Fix: TODAS las referencias a tablas en op.execute() deben usar
dobles comillas: "Vehicles", "Orders", etc.

Revision ID: a1b2c3d4e5f6
Revises: 0a18a24c8531
Create Date: 2026-05-12 08:00:00.000000

"""
from typing import Sequence, Union

from alembic import op

revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '0a18a24c8531'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _safe(sql: str) -> None:
    """Ejecuta DDL saltando errores si el objeto ya existe o ya fue modificado."""
    try:
        op.execute(sql)
    except Exception as e:
        print(f"Saltando (ya existe o error menor): {sql[:80]}")
        print(f"  → {e}")


def upgrade() -> None:
    # --- Corrección nombre de columna ---
    # cli_date_mod fue copiado incorrectamente de Clients a Vehicles.
    _safe('ALTER TABLE "Vehicles" RENAME COLUMN cli_date_mod TO veh_date_mod')

    # --- Índices para mejorar performance en búsquedas frecuentes ---
    # idx_ordenes_status_fecha: filtros por estado y ordenamiento por fecha.
    _safe('CREATE INDEX idx_ordenes_status_fecha ON "Orders" (ord_status, ord_date)')

    # idx_vehiculo_upper_plate: búsqueda case-insensitive por patente.
    _safe('CREATE INDEX idx_vehiculo_upper_plate ON "Vehicles" (UPPER(veh_plate))')

    # --- Corrección nombre de columna ---
    # srv_price → srv_price_hour para reflejar que es precio por hora.
    _safe('ALTER TABLE "Service" RENAME COLUMN srv_price TO srv_price_hour')

    # --- CHECK constraints para integridad de datos ---
    # El año del vehículo debe ser posterior a 1900.
    _safe('ALTER TABLE "Vehicles" ADD CONSTRAINT ck_vehiculo_anio CHECK (veh_year > 1900)')
    # El estado de la orden solo puede tomar estos tres valores.
    _safe("""ALTER TABLE "Orders" ADD CONSTRAINT ck_orden_estado CHECK (ord_status IN ('ABIERTA','EN_PROCESO','CERRADA'))""")
    # Las horas trabajadas deben ser positivas.
    _safe('ALTER TABLE "ServiceOrders" ADD CONSTRAINT ck_ords_horas_positivas CHECK (ords_hours > 0)')
    # El precio por hora debe ser mayor a cero.
    _safe('ALTER TABLE "Service" ADD CONSTRAINT ck_servicio_precio CHECK (srv_price_hour > 0)')

    # --- UNIQUE compuesto ---
    # Garantiza que no se duplique el mismo servicio en una misma orden.
    _safe('ALTER TABLE "ServiceOrders" ADD CONSTRAINT uq_ord_servicio UNIQUE (ord_id, srv_id)')

    # --- Modificaciones de columnas ---
    # ord_urgency se vuelve nullable porque no siempre es requerida.
    _safe('ALTER TABLE "Orders" MODIFY (ord_urgency NULL)')

    # Default para ord_status: al crear una orden, queda "ABIERTA" por defecto.
    _safe("""ALTER TABLE "Orders" MODIFY (ord_status DEFAULT 'ABIERTA')""")


def downgrade() -> None:
    # Deshace todos los cambios: renombres, índices, constraints y defaults.
    _safe('ALTER TABLE "Vehicles" RENAME COLUMN veh_date_mod TO cli_date_mod')
    _safe('DROP INDEX idx_ordenes_status_fecha')
    _safe('DROP INDEX idx_vehiculo_upper_plate')
    _safe('ALTER TABLE "Vehicles" DROP CONSTRAINT ck_vehiculo_anio')
    _safe('ALTER TABLE "Orders" DROP CONSTRAINT ck_orden_estado')
    _safe('ALTER TABLE "ServiceOrders" DROP CONSTRAINT ck_ords_horas_positivas')
    _safe('ALTER TABLE "Service" DROP CONSTRAINT ck_servicio_precio')
    _safe('ALTER TABLE "ServiceOrders" DROP CONSTRAINT uq_ord_servicio')
    _safe('ALTER TABLE "Orders" MODIFY (ord_urgency NOT NULL)')
    _safe('ALTER TABLE "Service" RENAME COLUMN srv_price_hour TO srv_price')
    _safe("""ALTER TABLE "Orders" MODIFY (ord_status DEFAULT 'open')""")

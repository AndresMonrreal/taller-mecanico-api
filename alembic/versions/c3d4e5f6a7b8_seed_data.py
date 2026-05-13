"""seed data para desarrollo y pruebas

NOTA sobre tabla "users":
- Modelo: __tablename__ = "users" (todo minúsculas)
- SQLAlchemy NO entrecomilla nombres todo-minúsculas en Oracle
- BD almacena como USERS (uppercase)
- En SQL raw: users (sin comillas) → Oracle busca USERS ✓
- NO usar "users" (entrecomillado minúscula) → busca users ≠ USERS ✗

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-05-12 09:00:00.000000

"""
from typing import Sequence, Union

from alembic import op

revision: str = 'c3d4e5f6a7b8'
down_revision: Union[str, None] = 'b2c3d4e5f6a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _safe(sql: str) -> None:
    try:
        op.execute(sql)
    except Exception as e:
        print(f"Saltando: {str(e)[:120]}")


def upgrade() -> None:
    _safe("""INSERT INTO "Sessions" (ses_id, ses_usuario) VALUES (1, 'admin')""")
    _safe("""INSERT INTO "Sessions" (ses_id, ses_usuario) VALUES (2, 'mecanico')""")
    _safe("""INSERT INTO "Sessions" (ses_id, ses_usuario) VALUES (3, 'recepcion')""")

    _safe("""INSERT INTO "Clients" (cli_id, cli_name, cli_phone, cli_email, ses_id) VALUES (1, 'Juan Pérez', '5551112233', 'juan@email.com', 1)""")
    _safe("""INSERT INTO "Clients" (cli_id, cli_name, cli_phone, cli_email, ses_id) VALUES (2, 'María García', '5554445566', 'maria@email.com', 1)""")
    _safe("""INSERT INTO "Clients" (cli_id, cli_name, cli_phone, cli_email, ses_id) VALUES (3, 'Carlos López', '5557778899', 'carlos@email.com', 1)""")

    _safe("""INSERT INTO "Vehicles" (veh_id, veh_plate, veh_brand, veh_model, veh_year, cli_id, ses_id) VALUES (1, 'ABC123', 'Toyota', 'Corolla', 2020, 1, 1)""")
    _safe("""INSERT INTO "Vehicles" (veh_id, veh_plate, veh_brand, veh_model, veh_year, cli_id, ses_id) VALUES (2, 'DEF456', 'Honda', 'Civic', 2019, 1, 1)""")
    _safe("""INSERT INTO "Vehicles" (veh_id, veh_plate, veh_brand, veh_model, veh_year, cli_id, ses_id) VALUES (3, 'GHI789', 'Nissan', 'Versa', 2021, 2, 1)""")
    _safe("""INSERT INTO "Vehicles" (veh_id, veh_plate, veh_brand, veh_model, veh_year, cli_id, ses_id) VALUES (4, 'JKL012', 'Mazda', '3', 2022, 2, 1)""")
    _safe("""INSERT INTO "Vehicles" (veh_id, veh_plate, veh_brand, veh_model, veh_year, cli_id, ses_id) VALUES (5, 'MNO345', 'Ford', 'Focus', 2018, 3, 1)""")

    _safe("""INSERT INTO "Service" (srv_id, srv_name, srv_price_hour, ses_id) VALUES (1, 'Cambio de Aceite', 150.00, 1)""")
    _safe("""INSERT INTO "Service" (srv_id, srv_name, srv_price_hour, ses_id) VALUES (2, 'Frenos', 250.00, 1)""")
    _safe("""INSERT INTO "Service" (srv_id, srv_name, srv_price_hour, ses_id) VALUES (3, 'Alineación', 200.00, 1)""")
    _safe("""INSERT INTO "Service" (srv_id, srv_name, srv_price_hour, ses_id) VALUES (4, 'Diagnóstico', 300.00, 1)""")

    _safe("""INSERT INTO "Orders" (ord_id, ord_date, ord_status, ord_urgency, ses_id, veh_id) VALUES (1, CURRENT_TIMESTAMP, 'ABIERTA', 'normal', 1, 1)""")
    _safe("""INSERT INTO "Orders" (ord_id, ord_date, ord_status, ord_urgency, ses_id, veh_id) VALUES (2, CURRENT_TIMESTAMP, 'EN_PROCESO', 'urgente', 2, 3)""")
    _safe("""INSERT INTO "Orders" (ord_id, ord_date, ord_status, ord_urgency, ses_id, veh_id) VALUES (3, CURRENT_TIMESTAMP - 2, 'CERRADA', 'normal', 3, 5)""")

    _safe("""INSERT INTO "ServiceOrders" (ord_id, srv_id, ords_hours, ords_total, ses_id) VALUES (1, 1, 2.0, 300.00, 1)""")
    _safe("""INSERT INTO "ServiceOrders" (ord_id, srv_id, ords_hours, ords_total, ses_id) VALUES (1, 3, 1.0, NULL, 1)""")
    _safe("""INSERT INTO "ServiceOrders" (ord_id, srv_id, ords_hours, ords_total, ses_id) VALUES (2, 2, 1.5, 375.00, 2)""")
    _safe("""INSERT INTO "ServiceOrders" (ord_id, srv_id, ords_hours, ords_total, ses_id) VALUES (2, 4, 2.0, 600.00, 2)""")
    _safe("""INSERT INTO "ServiceOrders" (ord_id, srv_id, ords_hours, ords_total, ses_id) VALUES (2, 1, 1.0, NULL, 2)""")
    _safe("""INSERT INTO "ServiceOrders" (ord_id, srv_id, ords_hours, ords_total, ses_id) VALUES (3, 1, 1.0, 150.00, 3)""")
    _safe("""INSERT INTO "ServiceOrders" (ord_id, srv_id, ords_hours, ords_total, ses_id) VALUES (3, 2, 2.0, 500.00, 3)""")
    _safe("""INSERT INTO "ServiceOrders" (ord_id, srv_id, ords_hours, ords_total, ses_id) VALUES (3, 4, 1.5, 450.00, 3)""")

    _safe("INSERT INTO users (usr_id, usr_username, usr_password, usr_rol, ses_id) VALUES (1, 'admin', '$2b$12$Fn3BAL2w4ZI6RSXnRhkJMuAQpfWT.I7lwDxGp0PK3qYGj8LyfICpK', 'admin', 1)")
    _safe("INSERT INTO users (usr_id, usr_username, usr_password, usr_rol, ses_id) VALUES (2, 'mecanico', '$2b$12$AiVMysxKsAO.YJ6lMTw/6.R6TeBt0KkBOVXUafIaQn9e9Qb.xTvBm', 'mecanico', 2)")
    _safe("INSERT INTO users (usr_id, usr_username, usr_password, usr_rol, ses_id) VALUES (3, 'recepcion', '$2b$12$TaFUOOlNo4lrX1Kd58xmY.XV4BfjJRo4qPEK/K4sCVetmmvBRyaBu', 'recepcion', 3)")


def downgrade() -> None:
    _safe("DELETE FROM users WHERE usr_id IN (1,2,3)")
    _safe("""DELETE FROM "ServiceOrders" WHERE ord_id IN (1,2,3)""")
    _safe("""DELETE FROM "Orders" WHERE ord_id IN (1,2,3)""")
    _safe("""DELETE FROM "Service" WHERE srv_id IN (1,2,3,4)""")
    _safe("""DELETE FROM "Vehicles" WHERE veh_id IN (1,2,3,4,5)""")
    _safe("""DELETE FROM "Clients" WHERE cli_id IN (1,2,3)""")
    _safe("""DELETE FROM "Sessions" WHERE ses_id IN (1,2,3)""")

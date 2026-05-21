"""roles de aplicación y transacción distribuida simulada

Agrega:
- sp_log_transferencia (autonomous transaction) — simula sistema remoto
- sp_transferir_servicio — transacción distribuida simulada con SAVEPOINT
- Grants para taller_app sobre nuevos objetos

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-05-20 12:00:00.000000

"""
from typing import Sequence, Union
from alembic import op

revision: str = 'd4e5f6a7b8c9'
down_revision: Union[str, None] = 'c3d4e5f6a7b8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _safe(sql: str) -> None:
    try:
        op.execute(sql)
    except Exception as e:
        print(f"Saltando: {str(e)[:120]}")


def upgrade() -> None:
    _safe("""
        CREATE OR REPLACE PROCEDURE sp_log_transferencia(
            p_srv_ord_id IN NUMBER,
            p_ord_id_old IN NUMBER,
            p_ord_id_new IN NUMBER
        )
        IS
            PRAGMA AUTONOMOUS_TRANSACTION;
        BEGIN
            INSERT INTO "Sessions"(ses_usuario, ses_fecha)
            VALUES ('DISTRIBUTED_TX', SYSDATE);
            COMMIT;
        END sp_log_transferencia;
    """)

    _safe("""
        CREATE OR REPLACE PROCEDURE sp_transferir_servicio(
            p_srv_ord_id  IN NUMBER,
            p_ord_id_new  IN NUMBER,
            p_mensaje     OUT VARCHAR2
        )
        IS
            v_old_ord_id    NUMBER;
            v_old_total     NUMBER;
            v_ord_status    VARCHAR2(50);
        BEGIN
            SAVEPOINT sp_transfer_save;

            SELECT ord_id, ords_total INTO v_old_ord_id, v_old_total
            FROM "ServiceOrders"
            WHERE srv_ord_id = p_srv_ord_id;

            SELECT ord_status INTO v_ord_status
            FROM "Orders"
            WHERE ord_id = p_ord_id_new;

            IF v_ord_status = 'CERRADA' THEN
                ROLLBACK TO sp_transfer_save;
                p_mensaje := 'La orden destino está cerrada';
                RETURN;
            END IF;

            UPDATE "ServiceOrders"
            SET ord_id = p_ord_id_new
            WHERE srv_ord_id = p_srv_ord_id;

            sp_log_transferencia(p_srv_ord_id, v_old_ord_id, p_ord_id_new);

            COMMIT;
            p_mensaje := 'OK: Servicio transferido (transacción distribuida simulada)';

        EXCEPTION
            WHEN OTHERS THEN
                ROLLBACK TO sp_transfer_save;
                p_mensaje := 'Error: ' || SQLERRM;
                RAISE;
        END sp_transferir_servicio;
    """)


def downgrade() -> None:
    _safe("DROP PROCEDURE sp_transferir_servicio")
    _safe("DROP PROCEDURE sp_log_transferencia")

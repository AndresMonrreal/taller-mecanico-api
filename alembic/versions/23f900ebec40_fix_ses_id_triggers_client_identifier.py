"""fix: triggers ses_id usan CLIENT_IDENTIFIER en vez de SESSIONID

SYS_CONTEXT('USERENV','SESSIONID') devuelve el ID de sesión de Oracle,
NO el ses_id de la tabla Sessions. Esto causaba ORA-02291 (FK violation).

Solución:
1. Python llama DBMS_SESSION.SET_IDENTIFIER(str(ses_id)) en cada request
2. Los triggers leen SYS_CONTEXT('USERENV','CLIENT_IDENTIFIER')
3. El valor ahora coincide con un ses_id real de la tabla Sessions ✅

Revision ID: 23f900ebec40
Revises: d4e5f6a7b8c9
Create Date: 2026-06-02 21:00:10.419396

"""
from typing import Sequence, Union

from alembic import op

revision: str = '23f900ebec40'
down_revision: Union[str, None] = 'd4e5f6a7b8c9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _safe(sql: str) -> None:
    try:
        op.execute(sql)
    except Exception as e:
        print(f"Saltando: {str(e)[:120]}")


def upgrade() -> None:
    # --- Recrear los 6 triggers de ses_id con CLIENT_IDENTIFIER ---
    # Ya no usan SYS_CONTEXT('USERENV','SESSIONID') porque ese valor
    # NO existe como registro en la tabla Sessions (ORA-02291).
    # Ahora leen CLIENT_IDENTIFIER que es seteado por Python vía
    # DBMS_SESSION.SET_IDENTIFIER(str(ses_id)) en dependencies.py.
    triggers = [
        ("trg_clients_ses_id", "Clients"),
        ("trg_vehicles_ses_id", "Vehicles"),
        ("trg_orders_ses_id", "Orders"),
        ("trg_serviceorders_ses_id", "ServiceOrders"),
        ("trg_service_ses_id", "Service"),
        ("trg_users_ses_id", "users"),
    ]
    for trg_name, tbl_name in triggers:
        _safe(f"""
            CREATE OR REPLACE TRIGGER {trg_name}
            BEFORE INSERT ON "{tbl_name}"
            FOR EACH ROW
            BEGIN
                IF \\:NEW.ses_id IS NULL THEN
                    \\:NEW.ses_id := TO_NUMBER(SYS_CONTEXT('USERENV', 'CLIENT_IDENTIFIER'));
                END IF;
            END {trg_name};
        """)

    # --- Actualizar sp_transferir_servicio con validación anti-duplicado ---
    # Mejora: verifica que el servicio no exista ya en la orden destino.
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
            v_srv_id        NUMBER;
            v_duplicado     NUMBER;
        BEGIN
            SAVEPOINT sp_transfer_save;

            SELECT ord_id, ords_total, srv_id INTO v_old_ord_id, v_old_total, v_srv_id
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

            SELECT COUNT(*) INTO v_duplicado
            FROM "ServiceOrders"
            WHERE ord_id = p_ord_id_new AND srv_id = v_srv_id;

            IF v_duplicado > 0 THEN
                ROLLBACK TO sp_transfer_save;
                p_mensaje := 'La orden destino ya tiene ese servicio registrado';
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
    # Revertir triggers a SYS_CONTEXT('SESSIONID') — NO RECOMENDADO
    triggers = [
        ("trg_clients_ses_id", "Clients"),
        ("trg_vehicles_ses_id", "Vehicles"),
        ("trg_orders_ses_id", "Orders"),
        ("trg_serviceorders_ses_id", "ServiceOrders"),
        ("trg_service_ses_id", "Service"),
        ("trg_users_ses_id", "users"),
    ]
    for trg_name, tbl_name in triggers:
        _safe(f"""
            CREATE OR REPLACE TRIGGER {trg_name}
            BEFORE INSERT ON "{tbl_name}"
            FOR EACH ROW
            BEGIN
                IF \\:NEW.ses_id IS NULL THEN
                    \\:NEW.ses_id := SYS_CONTEXT('USERENV', 'SESSIONID');
                END IF;
            END {trg_name};
        """)

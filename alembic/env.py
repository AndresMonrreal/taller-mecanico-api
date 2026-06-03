"""
Entorno de ejecución de Alembic para Base de Datos Oracle (ATP).

Configura la conexión a Oracle Autonomous Database usando:
  - Wallet (mTLS) para autenticación.
  - oracledb en modo thick (driver nativo).
  - DSN predefinido del servicio ATP.

Carga los modelos SQLAlchemy (app.models) para que Alembic pueda
detectar cambios en el metadata y generar migraciones automáticas.
"""

from logging.config import fileConfig
from sqlalchemy import create_engine, pool
from sqlalchemy.pool import StaticPool
from alembic import context
import sys, os
import oracledb

# Agrega el directorio raíz del proyecto al PYTHONPATH
# para poder importar app.core.config y app.models.
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.core.config import settings
from app.core.db import Base
import app.models

# Objeto de configuración de Alembic (lee de alembic.ini)
config = context.config

# Configura logging según alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata de SQLAlchemy: Alembic compara este metadata contra la BD
# para generar migraciones automáticas.
target_metadata = Base.metadata

# Ruta al wallet de Oracle ATP (mTLS)
wallet_path = os.path.abspath(settings.WALLET_LOCATION)

# DSN de conexión al servicio ATP (configurado manualmente)
dsn = "(description= (retry_count=20)(retry_delay=3)(address=(protocol=tcps)(port=1522)(host=adb.us-ashburn-1.oraclecloud.com))(connect_data=(service_name=g0b7cfb77ae7f8d_p1400zpt1kp7z3zp_tp.adb.oraclecloud.com))(security=(ssl_server_dn_match=yes)))"


def get_connection():
    """
    Crea una conexión directa a Oracle ATP usando oracledb.
    Se usa como 'creator' del engine de SQLAlchemy para evitar
    que SQLAlchemy maneje el pool de conexiones directamente.
    """
    return oracledb.connect(
        user=settings.DB_USER,
        password=settings.DB_PASS,
        dsn=dsn,
        wallet_location=wallet_path,
        wallet_password=settings.WALLET_PASSWORD
    )


def run_migrations_online():
    """
    Ejecuta las migraciones en modo online (conectado a la BD).
    Usa StaticPool porque la conexión se maneja externamente vía creator.
    """
    engine = create_engine(
        "oracle+oracledb://",
        creator=get_connection,
        poolclass=StaticPool
    )
    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


# Punto de entrada: Alembic llama este archivo.
# El modo offline (generar SQL sin conexión) no está implementado.
if context.is_offline_mode():
    pass
else:
    run_migrations_online()
from logging.config import fileConfig
from sqlalchemy import create_engine, pool
from sqlalchemy.pool import StaticPool
from alembic import context
import sys, os
import oracledb

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.core.config import settings
from app.core.db import Base
import app.models

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

wallet_path = os.path.abspath(settings.WALLET_LOCATION)

dsn = "(description= (retry_count=20)(retry_delay=3)(address=(protocol=tcps)(port=1522)(host=adb.us-ashburn-1.oraclecloud.com))(connect_data=(service_name=g0b7cfb77ae7f8d_p1400zpt1kp7z3zp_tp.adb.oraclecloud.com))(security=(ssl_server_dn_match=yes)))"

def get_connection():
    return oracledb.connect(
        user=settings.DB_USER,
        password=settings.DB_PASS,
        dsn=dsn,
        wallet_location=wallet_path,
        wallet_password=settings.WALLET_PASSWORD
    )

def run_migrations_online():
    engine = create_engine(
        "oracle+oracledb://",
        creator=get_connection,
        poolclass=StaticPool
    )
    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    pass
else:
    run_migrations_online()
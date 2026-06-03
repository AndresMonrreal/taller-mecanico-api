import oracledb
import os
from sqlalchemy import create_engine, pool, text
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import settings

# Ruta absoluta al wallet de Oracle ATP para conexión segura
wallet_path = os.path.abspath(settings.WALLET_LOCATION)

# DSN de conexión a Oracle Autonomous Database en la nube (ATP)
dsn = "(description= (retry_count=20)(retry_delay=3)(address=(protocol=tcps)(port=1522)(host=adb.us-ashburn-1.oraclecloud.com))(connect_data=(service_name=g0b7cfb77ae7f8d_p1400zpt1kp7z3zp_tp.adb.oraclecloud.com))(security=(ssl_server_dn_match=yes)))"


def get_connection():
    """Crea y retorna una conexión directa a Oracle usando oracledb con wallet."""
    return oracledb.connect(
        user=settings.DB_USER,
        password=settings.DB_PASS,
        dsn=dsn,
        wallet_location=wallet_path,
        wallet_password=settings.WALLET_PASSWORD
    )


# Motor de SQLAlchemy que usa la función creator para obtener conexiones Oracle
engine = create_engine(
    "oracle+oracledb://",
    creator=get_connection,
    pool_size=5,
    max_overflow=10
)

# Fábrica de sesiones locales para interactuar con la base de datos
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Clase base declarativa para todos los modelos SQLAlchemy
Base = declarative_base()


def get_db():
    """
    Generador de sesiones de base de datos para usar con dependencias de FastAPI.
    Cierra la sesión automáticamente al finalizar la request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        # Limpia CLIENT_IDENTIFIER para evitar que el pool de conexiones
        # reutilice el ses_id de otro usuario en la siguiente request
        try:
            db.execute(
                text("BEGIN DBMS_SESSION.SET_IDENTIFIER(NULL); END;")
            )
        except Exception:
            pass
        db.close()
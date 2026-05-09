import oracledb
import os
from sqlalchemy import create_engine, pool
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import settings

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

engine = create_engine(
    "oracle+oracledb://",
    creator=get_connection,
    pool_size=5,
    max_overflow=10
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
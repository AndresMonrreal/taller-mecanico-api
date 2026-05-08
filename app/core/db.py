import oracledb
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import settings

oracledb.init_oracle_client()

DATABASE_URL = (
    f"oracle+oracledb://{settings.DB_USER}:{settings.DB_PASS}"
    f"@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_SERVICE}"
    f"?wallet_location={settings.WALLET_LOCATION}"
    f"&wallet_password={settings.WALLET_PASSWORD}"
)

engine = create_engine(DATABASE_URL, pool_size=5, max_overflow=10)

@event.listens_for(engine, "checkout")
def set_session_context(dbapi_connection, connection_record, connection_proxy):
    cursor = dbapi_connection.cursor()
    cursor.execute("BEGIN NULL; END;")
    cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
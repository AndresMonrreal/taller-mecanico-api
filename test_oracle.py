import oracledb
from app.core.config import settings

try:
    conn = oracledb.connect(
        user=settings.DB_USER,
        password=settings.DB_PASS,
        dsn=f"{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_SERVICE}",
        wallet_location=settings.WALLET_LOCATION,
        wallet_password=settings.WALLET_PASSWORD
    )
    print("Conexion exitosa!")
    print(f"Version Oracle: {conn.version}")
    conn.close()
except Exception as e:
    print(f"Error: {e}")
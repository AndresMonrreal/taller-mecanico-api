import oracledb
import os
from app.core.config import settings

wallet_path = os.path.abspath(settings.WALLET_LOCATION)

dsn = f"""(description= (retry_count=20)(retry_delay=3)(address=(protocol=tcps)(port=1522)(host=adb.us-ashburn-1.oraclecloud.com))(connect_data=(service_name=g0b7cfb77ae7f8d_p1400zpt1kp7z3zp_tp.adb.oraclecloud.com))(security=(ssl_server_dn_match=yes)))"""

try:
    conn = oracledb.connect(
        user=settings.DB_USER,
        password=settings.DB_PASS,
        dsn=dsn,
        wallet_location=wallet_path,
        wallet_password=settings.WALLET_PASSWORD
    )
    print("Conexion exitosa!")
    print(f"Version: {conn.version}")
    conn.close()
except Exception as e:
    print(f"Error: {e}")
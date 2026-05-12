from sqlalchemy.orm import Session
from sqlalchemy import text

# Permisos en hexadecimal (bitmask)
PERM_VER     = 0x01   # 0001
PERM_CREAR   = 0x02   # 0010
PERM_EDITAR  = 0x04   # 0100
PERM_ELIMINAR = 0x08  # 1000
PERM_ADMIN   = 0xFF   # 1111 1111 - todos los permisos

# Roles predefinidos
ROLES = {
    "admin":     PERM_ADMIN,
    "mecanico":  PERM_VER | PERM_CREAR | PERM_EDITAR,   # 0x07
    "recepcion": PERM_VER | PERM_CREAR,                  # 0x03
    "cliente":   PERM_VER                                # 0x01
}

def tiene_permiso(rol: str, permiso: int) -> bool:
    mascara = ROLES.get(rol, 0)
    return bool(mascara & permiso)

def tiene_permiso_bd(db: Session, rol: str, permiso: int) -> bool:
    result = db.execute(
        text("SELECT fn_tiene_permiso(:rol, :permiso) FROM dual"),
        {"rol": rol, "permiso": permiso}
    ).scalar()
    return result == 1
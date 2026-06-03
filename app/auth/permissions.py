from sqlalchemy.orm import Session
from sqlalchemy import text

# Permisos en hexadecimal (bitmask) para control de acceso granular
PERM_VER     = 0x01   # 0001 - permiso de lectura/visualización
PERM_CREAR   = 0x02   # 0010 - permiso de creación
PERM_EDITAR  = 0x04   # 0100 - permiso de edición/modificación
PERM_ELIMINAR = 0x08  # 1000 - permiso de eliminación
PERM_ADMIN   = 0xFF   # 1111 1111 - todos los permisos (administrador total)

# Roles predefinidos del sistema y su máscara de permisos asociada
ROLES = {
    "admin":     PERM_ADMIN,
    "mecanico":  PERM_VER | PERM_CREAR | PERM_EDITAR,   # 0x07
    "recepcion": PERM_VER | PERM_CREAR,                  # 0x03
    "cliente":   PERM_VER                                # 0x01
}


def tiene_permiso(rol: str, permiso: int) -> bool:
    """
    Verifica si un rol tiene un permiso específico usando bitmask (en memoria).

    Args:
        rol: Nombre del rol a evaluar
        permiso: Máscara del permiso requerido (ej: PERM_EDITAR)

    Returns:
        True si el rol tiene el permiso, False en caso contrario
    """
    mascara = ROLES.get(rol, 0)
    return bool(mascara & permiso)


def tiene_permiso_bd(db: Session, rol: str, permiso: int) -> bool:
    """
    Verifica si un rol tiene un permiso llamando a la función Oracle fn_tiene_permiso.

    Args:
        db: Sesión de base de datos
        rol: Nombre del rol a evaluar
        permiso: Máscara del permiso requerido

    Returns:
        True si la función de BD retorna 1, False en caso contrario
    """
    result = db.execute(
        text("SELECT fn_tiene_permiso(:rol, :permiso) FROM dual"),
        {"rol": rol, "permiso": permiso}
    ).scalar()
    return result == 1
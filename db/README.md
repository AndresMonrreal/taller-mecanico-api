# 🗄️ Base de Datos — Oracle 23ai

> **Documentación técnica de los objetos SQL: procedimientos almacenados, triggers, vistas, restricciones, índices y sistema de permisos.**

---

## 📋 Índice

- [Modelo Relacional](#modelo-relacional)
- [Procedimiento Almacenado: `sp_cerrar_orden`](#procedimiento-almacenado-sp_cerrar_orden)
- [Triggers de Auditoría](#triggers-de-auditoría)
- [Vistas Complejas: `vw_resumen_clientes`](#vistas-complejas-vw_resumen_clientes)
- [Vistas Adicionales](#vistas-adicionales)
- [Restricciones e Índices](#restricciones-e-índices)
- [Roles y Permisos (Bitmask)](#roles-y-permisos-bitmask)
- [Funciones PL/SQL](#funciones-plsql)
- [Usuario de Base de Datos](#usuario-de-base-de-datos)
- [Seed Data](#seed-data)

---

## Modelo Relacional

### Diagrama Entidad-Relación

```
┌──────────────────┐       ┌───────────────────┐       ┌──────────────────┐
│    Sessions      │       │     Clients        │       │     Service      │
│──────────────────│       │────────────────────│       │──────────────────│
│ PK  ses_id       │──┐    │ PK  cli_id         │       │ PK  srv_id       │
│     ses_usuario  │  │    │     cli_name        │       │     srv_name     │
│     ses_fecha    │  │    │     cli_phone  (UQ) │       │     srv_price_hour│
└──────────────────┘  │    │     cli_email  (UQ) │       │     ses_id (FK)──┼──┐
                      │    │     cli_date_mod    │       │     srv_date_mod │  │
                      │    │     ses_id (FK)─────┼──┐    └──────────────────┘  │
                      │    └─────────┬───────────┘  │                          │
                      │              │              │                          │
                      │              │ 1:N          │                          │
                      │              ▼              │                          │
                      │    ┌──────────────────┐     │                          │
                      │    │    Vehicles       │     │                          │
                      │    │──────────────────│     │                          │
                      │    │ PK  veh_id       │     │                          │
                      │    │     veh_plate(UQ)│     │                          │
                      │    │     veh_brand    │     │                          │
                      │    │     veh_model    │     │                          │
                      │    │     veh_year     │     │                          │
                      │    │     cli_id (FK)──┼──┐  │                          │
                      │    │     ses_id (FK)──┼──┼──┼──────────────────────────┘
                      │    │     veh_date_mod │  │  │
                      │    └────────┬─────────┘  │  │
                      │             │            │  │
                      │             │ 1:N        │  │
                      │             ▼            │  │
                      │    ┌──────────────────┐  │  │
                      │    │     Orders        │  │  │
                      │    │──────────────────│  │  │
                      │    │ PK  ord_id       │  │  │
                      │    │     ord_date     │  │  │
                      │    │     ord_status   │  │  │
                      │    │     ord_urgency  │  │  │
                      │    │     ord_notes    │  │  │
                      │    │     ses_id (FK)──┼──┼──┘
                      │    │     veh_id (FK)──┼──┘
                      │    └────────┬─────────┘
                      │             │
                      │             │ 1:N
                      │             ▼
                      │    ┌──────────────────────────┐
                      │    │     ServiceOrders         │
                      │    │──────────────────────────│
                      │    │ PK  srv_ord_id            │
                      │    │     ord_id (FK) ─── (UQ)  │
                      │    │     srv_id (FK) ─── (UQ)  │
                      │    │     ords_hours             │
                      │    │     ords_total             │
                      │    │     ses_id (FK)────────────┼──┘
                      │    └──────────────────────────┘
                      │
                      ├──┐  ┌──────────────────┐
                      │  └──│     users         │
                      │     │──────────────────│
                      │     │ PK  usr_id       │
                      │     │     usr_username  │
                      │     │     usr_password  │
                      │     │     usr_rol       │
                      │     │     ses_id (FK)───┼───────┘
                      │     └──────────────────┘
                      │
                      │     ┌──────────────────────────┐
                      │     │     permisos_rol          │
                      │     │──────────────────────────│
                      │     │ PK  rol_id                │
                      │     │     rol_nombre (UQ)       │
                      │     │     permiso_bitmask       │
                      │     └──────────────────────────┘
                      │
                      └───── (ses_id FK en todas las tablas de negocio)
```

### Convenciones de Nomenclatura

| Elemento | Convención | Ejemplo |
|----------|------------|---------|
| Tablas | PascalCase con comillas dobles | `"Clients"`, `"Orders"`, `"ServiceOrders"` |
| Columnas | snake_case con prefijo de tabla | `cli_name`, `veh_plate`, `ord_status` |
| PK | `{tabla}_id` | `cli_id`, `ord_id` |
| FK | `{tabla}_id` (mismo nombre que PK referenciada) | `cli_id`, `ses_id` |
| Fechas de modificación | `{tabla}_date_mod` | `cli_date_mod`, `veh_date_mod` |
| CHECK constraints | `ck_{tabla}_{desc}` | `ck_orden_estado` |
| Índices | `idx_{tabla}_{columnas}` | `idx_ordenes_status_fecha` |
| Triggers | `trg_{tabla}_{accion}` | `trg_clients_ses_id` |
| Vistas | `vw_{desc}` | `vw_resumen_clientes` |
| Vista materializada | `vm_{desc}` | `vm_metricas_taller` |
| Funciones | `fn_{desc}` | `fn_tiene_permiso` |
| Procedimientos | `sp_{accion}_{objeto}` | `sp_cerrar_orden` |

---

## Procedimiento Almacenado: `sp_cerrar_orden`

### Código Completo

```sql
CREATE OR REPLACE PROCEDURE sp_cerrar_orden(
    p_ord_id   IN  NUMBER,
    p_mensaje  OUT VARCHAR2
)
IS
    v_status     VARCHAR2(50);
    v_pendientes NUMBER;
BEGIN
    -- 📌 Punto de restauración transaccional
    SAVEPOINT sp_save;

    -- Validar que la orden existe y su estado actual
    SELECT ord_status INTO v_status
    FROM "Orders"
    WHERE ord_id = p_ord_id;

    -- Rechazar si ya está cerrada
    IF v_status = 'CERRADA' THEN
        p_mensaje := 'La orden ya está cerrada';
        RETURN;
    END IF;

    -- Validar que todos los servicios tienen total calculado
    SELECT COUNT(*) INTO v_pendientes
    FROM "ServiceOrders"
    WHERE ord_id = p_ord_id AND ords_total IS NULL;

    IF v_pendientes > 0 THEN
        p_mensaje := 'Hay servicios sin total calculado';
        ROLLBACK TO sp_save;
        RETURN;
    END IF;

    -- Ejecutar el cierre
    UPDATE "Orders"
    SET ord_status = 'CERRADA'
    WHERE ord_id = p_ord_id;

    -- ✅ Confirmar transacción
    COMMIT;
    p_mensaje := 'Orden cerrada exitosamente';

EXCEPTION
    WHEN OTHERS THEN
        -- ❌ Revertir a savepoint en caso de error inesperado
        ROLLBACK TO sp_save;
        p_mensaje := SQLERRM;
        RAISE;
END sp_cerrar_orden;
```

### Análisis por Rúbrica

| Elemento | Implementación | Línea |
|----------|---------------|-------|
| **Parámetro IN** | `p_ord_id IN NUMBER` — recibe el ID de la orden a cerrar | 2 |
| **Parámetro OUT** | `p_mensaje OUT VARCHAR2` — retorna mensaje de resultado | 3 |
| **SAVEPOINT** | `SAVEPOINT sp_save` — punto de restauración al inicio | 8 |
| **Control Transaccional Explícito** | `COMMIT` en éxito (línea 34), `ROLLBACK TO sp_save` en error (línea 41) | 34, 41 |
| **Manejo de Excepciones** | `EXCEPTION WHEN OTHERS` — captura cualquier error, hace rollback y propaga con `RAISE` | 39-43 |
| **Validación de Negocio** | Orden ya cerrada (línea 16-19), servicios sin total (línea 23-28) | 16, 23 |
| **Transacción Atómica** | O se cierra completamente o no hay cambio alguno | 8-43 |

### Llamado desde FastAPI

```python
# app/routers/ordenes.py
@router.patch("/{ord_id}/cerrar")
def cerrar_orden(ord_id: int, db: Session = Depends(get_db)):
    result = db.execute(
        text("BEGIN sp_cerrar_orden(:ord_id, :mensaje); END;"),
        {"ord_id": ord_id, "mensaje": ""}
    )
    # Leer OUT parameter
    mensaje = result.returned_value
    return {"message": mensaje}
```

---

## Triggers de Auditoría

### Trigger de Auto-Asignación de `ses_id`

Seis triggers idénticos (uno por tabla con `ses_id`) que garantizan **trazabilidad completa** de qué sesión creó cada fila.

```sql
CREATE OR REPLACE TRIGGER trg_clients_ses_id
BEFORE INSERT ON "Clients"
FOR EACH ROW
BEGIN
    IF :NEW.ses_id IS NULL THEN
        :NEW.ses_id := SYS_CONTEXT('USERENV', 'SESSIONID');
    END IF;
END trg_clients_ses_id;
```

**Tablas cubiertas:** `Clients`, `Vehicles`, `Orders`, `ServiceOrders`, `Service`, `users`

### Compound Trigger: `trg_validar_cierre_orden`

```sql
CREATE OR REPLACE TRIGGER "TRG_VALIDAR_CIERRE_ORDEN"
FOR UPDATE OF ord_status ON "Orders"
COMPOUND TRIGGER
    TYPE ord_id_tab IS TABLE OF "Orders".ord_id%TYPE;
    v_ord_ids ord_id_tab := ord_id_tab();

    BEFORE EACH ROW IS
    BEGIN
        IF :NEW.ord_status = 'CERRADA' AND :OLD.ord_status != 'CERRADA' THEN
            v_ord_ids.EXTEND;
            v_ord_ids(v_ord_ids.LAST) := :NEW.ord_id;
        END IF;
    END BEFORE EACH ROW;

    AFTER STATEMENT IS
        v_pendientes NUMBER;
    BEGIN
        FOR i IN 1..v_ord_ids.COUNT LOOP
            SELECT COUNT(*) INTO v_pendientes
            FROM "ServiceOrders"
            WHERE ord_id = v_ord_ids(i) AND ords_total IS NULL;
            IF v_pendientes > 0 THEN
                RAISE_APPLICATION_ERROR(-20001,
                    'No se puede cerrar la orden ' || v_ord_ids(i) ||
                    ' porque tiene ' || v_pendientes || ' servicio(s) sin total');
            END IF;
        END LOOP;
    END AFTER STATEMENT;
END;
```

**¿Por qué COMPOUND TRIGGER?** Resuelve el problema de **tabla mutante** — Oracle no permite leer `ServiceOrders` en un `BEFORE ROW` trigger sobre `Orders` porque la tabla está mutando. El compound trigger recolecta los `ord_id` en la fase `BEFORE EACH ROW` y los valida en `AFTER STATEMENT`, cuando la tabla ya no está mutante.

---

## Vistas Complejas: `vw_resumen_clientes`

### Definición

```sql
CREATE OR REPLACE VIEW vw_resumen_clientes AS
SELECT
    c.cli_id,
    c.cli_name,

    -- Subconsulta: total de vehículos por cliente
    (SELECT COUNT(*)
     FROM "Vehicles" v
     WHERE v.cli_id = c.cli_id) AS total_vehiculos,

    -- JOIN agregado: total de órdenes
    COUNT(o.ord_id) AS total_ordenes,

    -- CASE: órdenes en estado CERRADA
    SUM(CASE WHEN o.ord_status = 'CERRADA' THEN 1 ELSE 0 END) AS ordenes_cerradas

FROM "Clients" c
LEFT JOIN "Orders" o
    ON o.veh_id IN (
        SELECT veh_id
        FROM "Vehicles" v2
        WHERE v2.cli_id = c.cli_id
    )
GROUP BY c.cli_id, c.cli_name;
```

### Técnicas Empleadas

| Técnica | Uso |
|---------|-----|
| **Subconsulta escalar** | `(SELECT COUNT(*) FROM Vehicles ...)` — cuenta vehículos por cliente |
| **LEFT JOIN** | Garantiza que clientes sin órdenes también aparezcan (total_ordenes = 0) |
| **Subconsulta en JOIN** | `ON o.veh_id IN (SELECT veh_id FROM Vehicles WHERE ...)` — relaciona órdenes con clientes a través de vehículos |
| **CASE + SUM** | Convierte condición booleana en contador numérico |
| **GROUP BY** | Agrega por cliente para obtener métricas consolidadas |

### Consumo desde API

```python
# app/routers/clientes.py
@router.get("/vista/resumen")
def get_resumen_clientes(db: Session = Depends(get_db)):
    result = db.execute(text("SELECT * FROM vw_resumen_clientes")).fetchall()
    return {"data": [dict(row._mapping) for row in result]}
```

---

## Vistas Adicionales

### Vista Simple: `vw_ordenes_activas`

```sql
CREATE OR REPLACE VIEW vw_ordenes_activas AS
SELECT ord_id, veh_id, ord_status, ord_date, ord_urgency
FROM "Orders"
WHERE ord_status IN ('ABIERTA', 'EN_PROCESO');
```

Filtra las órdenes que aún están en progreso, excluyendo las cerradas.

### Vista Materializada: `vm_metricas_taller`

```sql
CREATE MATERIALIZED VIEW vm_metricas_taller
BUILD IMMEDIATE
REFRESH COMPLETE ON DEMAND
AS
SELECT
    TRUNC(ord_date) AS dia,
    COUNT(*)        AS total_ordenes,
    SUM(CASE WHEN ord_status = 'CERRADA' THEN 1 ELSE 0 END) AS cerradas
FROM "Orders"
GROUP BY TRUNC(ord_date);
```

**Propósito:** Dashboard de métricas diarias. Se refresca bajo demanda (`REFRESH COMPLETE ON DEMAND`), ideal para reportes periódicos sin impacto en operaciones transaccionales.

---

## Restricciones e Índices

### CHECK Constraints

| Nombre | Tabla | Expresión | Propósito |
|--------|-------|-----------|-----------|
| `ck_orden_estado` | `Orders` | `ord_status IN ('ABIERTA','EN_PROCESO','CERRADA')` | 🔒 Estado válido |
| `ck_vehiculo_anio` | `Vehicles` | `veh_year > 1900` | 🔒 Año razonable |
| `ck_ords_horas_positivas` | `ServiceOrders` | `ords_hours > 0` | 🔒 Horas positivas |
| `ck_servicio_precio` | `Service` | `srv_price_hour > 0` | 🔒 Precio positivo |

### UNIQUE Constraints

| Nombre | Tabla | Columnas | Propósito |
|--------|-------|----------|-----------|
| `uq_clients_email` | `Clients` | `cli_email` | Email único |
| `uq_clients_phone` | `Clients` | `cli_phone` | Teléfono único |
| `uq_vehiculos_plate` | `Vehicles` | `veh_plate` | Placa única |
| `uq_service_name` | `Service` | `srv_name` | Nombre de servicio único |
| `uq_users_username` | `users` | `usr_username` | Username único |
| **`uq_ord_servicio`** | **`ServiceOrders`** | **(ord_id, srv_id)** | ⭐ **UNIQUE compuesto** — un servicio no puede asignarse dos veces a la misma orden |

### Índices

#### 🏆 Índice Compuesto: `idx_ordenes_status_fecha`

```sql
CREATE INDEX idx_ordenes_status_fecha
ON "Orders"(ord_status, ord_date);
```

**Propósito:** Optimiza las búsquedas más frecuentes:
- `SELECT * FROM Orders WHERE ord_status = 'ABIERTA'` → filtro por status
- Dashboard de órdenes activas ordenadas por fecha
- Consultas de la vista `vw_ordenes_activas`

#### 🏆 Índice Funcional: `idx_vehiculo_upper_plate`

```sql
CREATE INDEX idx_vehiculo_upper_plate
ON "Vehicles"(UPPER(veh_plate));
```

**Propósito:** Búsqueda **case-insensitive** por placa. Permite que:
```sql
SELECT * FROM "Vehicles" WHERE UPPER(veh_plate) LIKE '%ABC%'
```
use el índice en lugar de un full table scan.

### Implementación desde SQLAlchemy

```python
# app/models/orden.py
class Order(Base):
    __tablename__ = "Orders"
    __table_args__ = (
        CheckConstraint(
            "ord_status IN ('ABIERTA','EN_PROCESO','CERRADA')",
            name="ck_orden_estado"
        ),
        Index("idx_ordenes_status_fecha", "ord_status", "ord_date"),
    )
```

---

## Roles y Permisos (Bitmask)

### Arquitectura de Seguridad

```
┌─────────────────────────────────────────────────────────────────┐
│                    Sistema de Permisos por Bitmask               │
│                                                                 │
│  MÁSCARAS HEXADECIMALES:                                        │
│                                                                 │
│    PERM_VER     = 0x01  (0001)  →  Permite consultar            │
│    PERM_CREAR   = 0x02  (0010)  →  Permite crear registros      │
│    PERM_EDITAR  = 0x04  (0100)  →  Permite editar registros     │
│    PERM_ELIMINAR = 0x08 (1000)  →  Permite eliminar registros   │
│    PERM_ADMIN   = 0xFF  (11111111) →  Todos los permisos         │
│                                                                 │
│  ROLES PREDEFINIDOS:                                             │
│                                                                 │
│    admin     → 0xFF  (255)  →  Todos los permisos                │
│    mecanico  → 0x07  (7)    →  VER + CREAR + EDITAR              │
│    recepcion → 0x03  (3)    →  VER + CREAR                       │
│    cliente   → 0x01  (1)    →  VER solamente                     │
└─────────────────────────────────────────────────────────────────┘
```

### Tabla `permisos_rol`

```sql
CREATE TABLE permisos_rol (
    rol_id          NUMBER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    rol_nombre      VARCHAR2(50) NOT NULL UNIQUE,
    permiso_bitmask NUMBER(3) NOT NULL
);

-- Seed de roles con máscaras hexadecimales
INSERT INTO permisos_rol (rol_nombre, permiso_bitmask) VALUES ('admin',     255);  -- 0xFF
INSERT INTO permisos_rol (rol_nombre, permiso_bitmask) VALUES ('mecanico',   7);   -- 0x07
INSERT INTO permisos_rol (rol_nombre, permiso_bitmask) VALUES ('recepcion',  3);   -- 0x03
INSERT INTO permisos_rol (rol_nombre, permiso_bitmask) VALUES ('cliente',    1);   -- 0x01
```

### Función de Validación: `fn_tiene_permiso`

```sql
CREATE OR REPLACE FUNCTION fn_tiene_permiso(
    p_rol     IN VARCHAR2,
    p_permiso IN NUMBER
) RETURN NUMBER
IS
    v_mask NUMBER(3);
BEGIN
    SELECT permiso_bitmask INTO v_mask
    FROM permisos_rol
    WHERE rol_nombre = p_rol;

    -- BITAND: operación AND a nivel de bits
    -- Si el bit solicitado está encendido en la máscara → tiene permiso
    IF BITAND(v_mask, p_permiso) = p_permiso THEN
        RETURN 1;  -- ✅ Tiene permiso
    ELSE
        RETURN 0;  -- ❌ No tiene permiso
    END IF;
EXCEPTION
    WHEN NO_DATA_FOUND THEN
        RETURN 0;  -- Rol no existe → denegar
END fn_tiene_permiso;
```

### Validación desde Python/FastAPI

```python
# app/auth/permissions.py
PERM_VER      = 0x01  # 0001
PERM_CREAR    = 0x02  # 0010
PERM_EDITAR   = 0x04  # 0100
PERM_ELIMINAR = 0x08  # 1000
PERM_ADMIN    = 0xFF  # 1111 1111

def tiene_permiso_bd(db: Session, rol: str, permiso: int) -> bool:
    """Verifica permiso llamando a la función Oracle fn_tiene_permiso"""
    result = db.execute(
        text("SELECT fn_tiene_permiso(:rol, :permiso) FROM dual"),
        {"rol": rol, "permiso": permiso}
    ).scalar()
    return result == 1
```

### Uso como Dependencia

```python
# app/dependencies.py
def require_permiso(permiso: int):
    def checker(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
        if not tiene_permiso_bd(db, current_user.usr_rol, permiso):
            raise HTTPException(
                status_code=403,
                detail="Sin permisos suficientes"
            )
        return current_user
    return checker

# Proteger endpoint:
@router.delete("/{cli_id}")
def delete_cliente(
    cli_id: int,
    current_user: User = Depends(require_permiso(PERM_ELIMINAR)),
    db: Session = Depends(get_db)
):
    ...
```

---

## Funciones PL/SQL

### `fn_calcular_total_orden`

```sql
CREATE OR REPLACE FUNCTION fn_calcular_total_orden(
    p_ord_id IN NUMBER
) RETURN NUMBER
IS
    v_total NUMBER(10,2);
BEGIN
    SELECT COALESCE(SUM(ords_total), 0) INTO v_total
    FROM "ServiceOrders"
    WHERE ord_id = p_ord_id;
    RETURN v_total;
END fn_calcular_total_orden;
```

**Uso:**
```sql
SELECT fn_calcular_total_orden(1) FROM dual;
```
```python
# FastAPI (app/routers/ordenes.py)
@router.get("/{ord_id}/total")
def get_orden_total(ord_id: int, db: Session = Depends(get_db)):
    total = db.execute(
        text("SELECT fn_calcular_total_orden(:ord_id) FROM dual"),
        {"ord_id": ord_id}
    ).scalar()
    return {"ord_id": ord_id, "total": float(total)}
```

---

## Usuario de Base de Datos

Principio de **mínimos privilegios** — el usuario `taller_app` solo tiene lo necesario para operar:

```sql
CREATE USER taller_app IDENTIFIED BY "TallerApp2026!";
GRANT CONNECT TO taller_app;
GRANT CREATE SESSION TO taller_app;

-- DML en tablas de negocio (sin DDL)
GRANT SELECT, INSERT, UPDATE, DELETE ON "Clients" TO taller_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON "Vehicles" TO taller_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON "Orders" TO taller_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON "ServiceOrders" TO taller_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON "Service" TO taller_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON "Sessions" TO taller_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON "users" TO taller_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON permisos_rol TO taller_app;

-- Ejecución de PL/SQL (sin modificación)
GRANT EXECUTE ON fn_tiene_permiso TO taller_app;
GRANT EXECUTE ON fn_calcular_total_orden TO taller_app;
GRANT EXECUTE ON sp_cerrar_orden TO taller_app;

-- Consulta de vistas
GRANT SELECT ON vw_resumen_clientes TO taller_app;
GRANT SELECT ON vw_ordenes_activas TO taller_app;
GRANT SELECT ON vm_metricas_taller TO taller_app;

-- Cuota de almacenamiento
ALTER USER taller_app QUOTA 100M ON USERS;
```

---

## Seed Data

Datos de prueba insertados por la migración `c3d4e5f6a7b8_seed_data.py`:

| Tabla | Filas | Detalle |
|-------|-------|---------|
| `Sessions` | 3 | admin, mecanico, recepcion |
| `Clients` | 3 | Juan Pérez, María García, Carlos López |
| `Vehicles` | 5 | 2 de Juan, 2 de María, 1 de Carlos |
| `Service` | 4 | Cambio de Aceite, Frenos, Alineación, Diagnóstico |
| `Orders` | 3 | 1 ABIERTA, 1 EN_PROCESO, 1 CERRADA |
| `ServiceOrders` | 8 | 2-3 servicios por orden (1 con `ords_total = NULL` para testing) |
| `users` | 3 | admin/admin123, mecanico/mec123, recepcion/rec123 (bcrypt) |
| `permisos_rol` | 4 | admin(0xFF), mecanico(0x07), recepcion(0x03), cliente(0x01) |

---

## Resumen de Objetos PL/SQL

| Objeto | Tipo | Líneas | Propósito |
|--------|------|--------|-----------|
| `sp_cerrar_orden` | PROCEDURE | 35 | Cierre transaccional de órdenes |
| `fn_calcular_total_orden` | FUNCTION | 10 | Suma de totales por orden |
| `fn_tiene_permiso` | FUNCTION | 18 | Validación de bitmask permissions |
| `vw_resumen_clientes` | VIEW | — | Métricas de clientes (compleja) |
| `vw_ordenes_activas` | VIEW | — | Órdenes en progreso (simple) |
| `vm_metricas_taller` | MATERIALIZED VIEW | — | Dashboard diario |
| `trg_clients_ses_id` | TRIGGER | 7 | Auto-asignación ses_id |
| `trg_vehicles_ses_id` | TRIGGER | 7 | Auto-asignación ses_id |
| `trg_orders_ses_id` | TRIGGER | 7 | Auto-asignación ses_id |
| `trg_serviceorders_ses_id` | TRIGGER | 7 | Auto-asignación ses_id |
| `trg_service_ses_id` | TRIGGER | 7 | Auto-asignación ses_id |
| `trg_users_ses_id` | TRIGGER | 7 | Auto-asignación ses_id |
| `TRG_VALIDAR_CIERRE_ORDEN` | COMPOUND TRIGGER | 25 | Validación anti-mutante |

---

## Archivos de Migración

| Archivo | Contenido |
|---------|-----------|
| `alembic/versions/0a18a24c8531_tablas_iniciales.py` | Creación de 7 tablas con SQLAlchemy |
| `alembic/versions/a1b2c3d4e5f6_correcciones_modelo.py` | Renombrar columnas, CHECK constraints, índices, UNIQUE compuesto |
| `alembic/versions/b2c3d4e5f6a7_plsql_objects.py` | Todos los objetos PL/SQL (SP, funciones, vistas, triggers, tabla permisos) |
| `alembic/versions/c3d4e5f6a7b8_seed_data.py` | Seed data de prueba |
| `db/create_taller_app_user.sql` | Script para crear usuario con privilegios mínimos |

---

<div align="center">
  <sub>Oracle 23ai · FastAPI · SQLAlchemy 2.x · Documentación técnica para evaluación</sub>
</div>

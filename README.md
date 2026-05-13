# Taller Mecánico API — Backend

> **API RESTful con FastAPI + Oracle 23ai para la gestión integral de talleres automotrices**  
> Arquitectura en capas con autenticación JWT, control transaccional explícito y permisos por bitmask.

---

## Índice

- [Estructura del Proyecto](#estructura-del-proyecto)
- [Arquitectura en Capas](#arquitectura-en-capas)
- [Control Transaccional](#control-transaccional)
- [Manejo de Errores ORA-01722 y ORA-02290](#manejo-de-errores-ora-01722-y-ora-02290)
- [Modelos de Datos](#modelos-de-datos)
- [Endpoints de la API](#endpoints-de-la-api)
- [Autenticación y Permisos](#autenticación-y-permisos)
- [Guía de Inicio Rápido](#guía-de-inicio-rápido)
- [Dependencias Principales](#dependencias-principales)

---

## Estructura del Proyecto

```
taller-mecanico-api/
│
├── app/
│   ├── main.py                          #  Punto de entrada FastAPI
│   ├── dependencies.py                  #  Inyección de dependencias (auth)
│   │
│   ├── core/
│   │   ├── config.py                    # Settings desde variables de entorno
│   │   ├── db.py                        # Engine + Session Oracle (Wallet mTLS)
│   │   └── errors.py                    # Manejadores globales de excepción
│   │
│   ├── auth/
│   │   ├── jwt.py                       #  HS256 tokens + bcrypt hashing
│   │   └── permissions.py               #  Bitmask constants (0x01..0xFF)
│   │
│   ├── models/                          #  SQLAlchemy 2.x ORM (8 modelos)
│   │   ├── __init__.py
│   │   ├── cliente.py                   # Client
│   │   ├── vehiculo.py                  # Vehicle
│   │   ├── orden.py                     # Order (ck_orden_estado + idx compuesto)
│   │   ├── orden_servicio.py            # ServiceOrder (UNIQUE compuesto)
│   │   ├── servicio.py                  # Service
│   │   ├── sesion.py                    # Session (ses_id)
│   │   ├── users.py                     # User (JWT auth)
│   │   └── permiso_rol.py              # Rol+Bitmask (modelo BD)
│   │
│   ├── schemas/                         #  Pydantic v2 (Base / Create / Out)
│   │   ├── cliente.py
│   │   ├── vehiculo.py
│   │   ├── orden.py
│   │   ├── servicio.py
│   │   ├── users.py
│   │   └── pagination.py                # Pagination<T> genérico
│   │
│   ├── crud/                            #  Capa de acceso a datos
│   │   ├── base.py                      # CRUDBase<T> genérico
│   │   ├── cliente.py                   # CRUDCliente
│   │   ├── vehiculo.py                  # CRUDVehicle
│   │   ├── orden.py                     # CRUDOrden (con SAVEPOINT)
│   │   └── servicio.py                  # CRUDService
│   │
│   ├── routers/                         #  Endpoints REST
│   │   ├── auth.py                      # /api/v1/auth/*
│   │   ├── clientes.py                  # /api/v1/clients/*
│   │   ├── vehiculos.py                 # /api/v1/vehiculos/*
│   │   ├── ordenes.py                   # /api/v1/ordenes/*
│   │   ├── servicios.py                 # /api/v1/servicios/*
│   │   └── ia.py                        # /api/v1/ia/* (OpenAI)
│   │
│   ├── middleware/
│   │   └── logging_middleware.py        #  Request logging (method, path, status, ms)
│   │
│   └── services/
│       └── claude_service.py            #  Integración OpenAI
│
├── db/
│   ├── create_taller_app_user.sql       #  Usuario BD con mínimos privilegios
│   └── README.md                        # Documentación de base de datos
│
├── alembic/                             #  Migraciones
│   ├── versions/
│   │   ├── 0a18a24c8531_tablas_iniciales.py
│   │   ├── a1b2c3d4e5f6_correcciones_modelo.py
│   │   ├── b2c3d4e5f6a7_plsql_objects.py
│   │   └── c3d4e5f6a7b8_seed_data.py
│   ├── env.py
│   └── script.py.mako
│
├── seeds/
│   └── seed.py                          #  Seed script vacío (seed via Alembic)
│
├── wallet/                              #  Oracle Wallet (mTLS)
├── venv/                                #  Entorno virtual Python
│
├── test_oracle.py                       #  Test de conectividad Oracle
├── requirements.txt                     #  Dependencias Python
├── alembic.ini                          #  Configuración Alembic
├── .env                                 #  Variables de entorno (gitignored)
├── .gitignore
└── OPENCODE.md                          #  Guía de convenciones del proyecto
```

---

## Arquitectura en Capas

```
                    ┌─────────────────────────────┐
                    │      Cliente HTTP            │
                    │   (Axios + JWT Bearer)       │
                    └─────────────┬───────────────┘
                                  │
                    ┌─────────────▼───────────────┐
                    │       main.py (FastAPI)      │
                    │  ┌─────────────────────────┐ │
                    │  │  CORS · Logging · Error  │ │
                    │  │   Handlers (val/db/gen)  │ │
                    │  └─────────────────────────┘ │
                    └─────────────┬───────────────┘
                                  │
                    ┌─────────────▼───────────────┐
                    │      dependencies.py         │
                    │  get_current_user()          │
                    │  require_permiso(bitmask)    │
                    └─────────────┬───────────────┘
                                  │
                    ┌─────────────▼───────────────┐
                    │         Routers              │
                    │  Validación → Auth → Lógica  │
                    └─────────────┬───────────────┘
                                  │
                    ┌─────────────▼───────────────┐
                    │     CRUD Layer (SQLAlchemy)  │
                    │  CRUDBase<T> → específicos   │
                    │  SAVEPOINT (begin_nested)    │
                    └─────────────┬───────────────┘
                                  │
                    ┌─────────────▼───────────────┐
                    │   Oracle 23ai (oracledb)     │
                    │  Tablas · Vistas · SP · Trig │
                    │  Wallet mTLS · Pool (5-10)   │
                    └─────────────────────────────┘
```

### Flujo de una Petición Típica

```
PATCH /api/v1/ordenes/1/cerrar
    │
    ├─ 1. Logging Middleware → "PATCH /api/v1/ordenes/1/cerrar -> ..."
    │
    ├─ 2. Error Handlers → atrapan cualquier excepción no capturada
    │
    ├─ 3. Router (ordenes.py)
    │      └─ Valida path param {ord_id: int}
    │
    ├─ 4. Dependencies
    │      ├─ get_current_user() → decodifica JWT, busca en BD
    │      └─ require_permiso(PERM_EDITAR) → verifica bitmask vía fn_tiene_permiso
    │
    ├─ 5. Core (SQLAlchemy)
    │      └─ db.execute(text("BEGIN sp_cerrar_orden(:id, :msg); END;"), ...)
    │
    ├─ 6. Oracle
    │      └─ sp_cerrar_orden(IN p_ord_id, OUT p_mensaje)
    │           ├─ SAVEPOINT sp_save
    │           ├─ Validar estado ≠ CERRADA
    │           ├─ Validar servicios sin total
    │           ├─ UPDATE ord_status = 'CERRADA'
    │           └─ COMMIT · EXCEPTION → ROLLBACK TO sp_save
    │
    └─ 7. Response JSON → {"message": "Orden cerrada exitosamente"}
```

---

## Control Transaccional

### Problema: Autocommit por Defecto

Por defecto, SQLAlchemy con `sessionmaker(autocommit=False)` requiere `commit()` explícito, pero ciertas operaciones que involucran **múltiples pasos** necesitan protección atómica.

###  SAVEPOINT en `crud/orden.py` — `create_with_services()`

```python
def create_with_services(self, db: Session, order_data: dict, services: list[dict]):
    try:
        #  SAVEPOINT explícito — punto de restauración
        with db.begin_nested():  # ← SAVEPOINT
            # 1. Crear la orden
            db_order = Order(**order_data)
            db.add(db_order)
            db.flush()  # Obtener ord_id sin commit

            # 2. Crear cada servicio asociado
            for srv in services:
                service = db.query(Service).get(srv["srv_id"])
                total = srv["ords_hours"] * service.srv_price_hour
                so = ServiceOrder(
                    ord_id=db_order.ord_id,
                    srv_id=srv["srv_id"],
                    ords_hours=srv["ords_hours"],
                    ords_total=total,
                )
                db.add(so)

        #  Si todo OK → commit del savepoint y la transacción padre
        db.commit()

    except Exception:
        #  Error → rollback automático de begin_nested()
        #    (solo revierte el savepoint, no la transacción padre)
        db.rollback()
        raise
```

###  SAVEPOINT en `sp_cerrar_orden` (Oracle)

```sql
CREATE OR REPLACE PROCEDURE sp_cerrar_orden(
    p_ord_id   IN NUMBER,
    p_mensaje  OUT VARCHAR2
) IS
    v_status     VARCHAR2(50);
    v_pendientes NUMBER;
BEGIN
    SAVEPOINT sp_save;              --  Punto de restauración

    SELECT ord_status INTO v_status FROM "Orders" WHERE ord_id = p_ord_id;
    IF v_status = 'CERRADA' THEN
        p_mensaje := 'La orden ya está cerrada';
        RETURN;
    END IF;

    SELECT COUNT(*) INTO v_pendientes
    FROM "ServiceOrders" WHERE ord_id = p_ord_id AND ords_total IS NULL;

    IF v_pendientes > 0 THEN
        ROLLBACK TO sp_save;        --  Revertir cambios parciales
        p_mensaje := 'Hay servicios sin total calculado';
        RETURN;
    END IF;

    UPDATE "Orders" SET ord_status = 'CERRADA' WHERE ord_id = p_ord_id;
    COMMIT;                          --  Confirmar transacción
    p_mensaje := 'Orden cerrada exitosamente';

EXCEPTION
    WHEN OTHERS THEN
        ROLLBACK TO sp_save;        --  Revertir en cualquier error
        p_mensaje := SQLERRM;
        RAISE;
END sp_cerrar_orden;
```

### Comparación de Estrategias

| Estrategia | Lugar | Uso | Efecto |
|-----------|-------|-----|--------|
| `db.commit()` | CRUD (Python) | Operaciones simples (crear/editar/eliminar un registro) | Persiste en BD |
| `db.begin_nested()` | CRUD (Python) | `create_with_services()` — múltiples inserts relacionados | Rollback parcial sin afectar transacción padre |
| `SAVEPOINT ... ROLLBACK TO` | Oracle PL/SQL | `sp_cerrar_orden` — validaciones + UPDATE crítico | Reversión atómica dentro del SP |
| `EXCEPTION ... ROLLBACK TO ... RAISE` | Oracle PL/SQL | `sp_cerrar_orden` | Manejo robusto de errores inesperados |

---

## Manejo de Errores ORA-01722 y ORA-02290

### ORA-01722: Conversión Numérica Inválida

**Causa:** Ocurre cuando se intenta insertar un valor no numérico en una columna numérica, por ejemplo al enviar un string en un campo `NUMBER`.

**Solución implementada:**

```python
# app/core/errors.py — Manejador global de SQLAlchemyError
@router.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request, exc: SQLAlchemyError):
    error_msg = str(exc.__cause__) if exc.__cause__ else str(exc)

    if "ORA-01722" in error_msg:
        return JSONResponse(
            status_code=400,
            content={"detail": "Error de conversión numérica. Verifica que los valores numéricos (precios, horas, años) sean válidos."}
        )

    if "ORA-02290" in error_msg:
        constraint = extraer_nombre_constraint(error_msg)
        return JSONResponse(
            status_code=400,
            content={"detail": f"Restricción de base de datos violada: {constraint}. Revisa los valores ingresados."}
        )

    return JSONResponse(
        status_code=500,
        content={"detail": "Error interno de base de datos."}
    )
```

**Prevención adicional en Schemas (Pydantic):**

```python
# app/schemas/vehiculo.py
class VehicleCreate(VehicleBase):
    veh_year: int = Field(gt=1900, lt=2100)   # Validación temprana
    cli_id: int

# app/schemas/servicio.py
class ServiceCreate(ServiceBase):
    srv_price_hour: Decimal = Field(gt=0)       # Rechazar antes de llegar a BD
```

### ORA-02290: CHECK Constraint Violada

**Causa:** Ocurre cuando un INSERT o UPDATE viola una `CHECK CONSTRAINT` definida en la tabla.

**Solución implementada — Constraints relevantes:**

```python
# app/models/orden.py
class Order(Base):
    __tablename__ = "Orders"
    __table_args__ = (
        CheckConstraint(
            "ord_status IN ('ABIERTA','EN_PROCESO','CERRADA')",
            name="ck_orden_estado"              # ⬅ORA-02290 si status inválido
        ),
        Index("idx_ordenes_status_fecha", "ord_status", "ord_date"),
    )
```

```python
# app/models/vehiculo.py
class Vehicle(Base):
    __tablename__ = "Vehicles"
    __table_args__ = (
        CheckConstraint(
            "veh_year > 1900",
            name="ck_vehiculo_anio"             # ORA-02290 si año ≤ 1900
        ),
    )
```

### Mapa de Errores y Respuestas HTTP

| Error Oracle | Causa Típica | Código HTTP | Mensaje al Usuario |
|-------------|-------------|-------------|-------------------|
| ORA-01722 | String en campo numérico | `400` | "Error de conversión numérica. Verifica los valores ingresados." |
| ORA-02290 | CHECK constraint violada | `400` | "Restricción violada: ck_orden_estado. Estado no válido." |
| ORA-00001 | UNIQUE constraint violada | `409` | "Ya existe un registro con ese valor único." |
| ORA-02291 | FK no encontrada | `404` | "El registro relacionado no existe." |
| ORA-20001 | Compound trigger | `400` | "No se puede cerrar la orden: tiene servicios sin total." |

---

## Modelos de Datos

### Diagrama de Clases (SQLAlchemy)

```
┌────────────────────────────────────────────────────────────────┐
│                         ORM Models                              │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  Session    ←── ses_id ──→  User      PermisoRol              │
│  ─────────                    ─────     ──────────              │
│  ses_id (PK)                  usr_id    rol_id (PK)             │
│  ses_usuario                  usr_username  rol_nombre          │
│  ses_fecha                    usr_password  permiso_bitmask     │
│                               usr_rol                          │
│                               ses_id (FK)                      │
│  Client ←── cli_id ──→ Vehicle ←── veh_id ──→ Order           │
│  ───────                   ───────             ──────           │
│  cli_id (PK)               veh_id (PK)        ord_id (PK)      │
│  cli_name    ─────────     veh_plate (UQ)      ord_date         │
│  cli_phone   │ 1:N         veh_brand           ord_status ck │
│  cli_email   │             veh_model           ord_urgency      │
│  cli_date_mod│             veh_year    ck    ord_notes       │
│  ses_id (FK) │             cli_id (FK)          ses_id (FK)     │
│              │             ses_id (FK)          veh_id (FK)     │
│              │             veh_date_mod                        │
│              │                                     │           │
│              │             Service ←── srv_id ─────┤ 1:N       │
│              │             ───────                  │           │
│              │             srv_id (PK)              ▼           │
│              │             srv_name (UQ)       ServiceOrder    │
│              │             srv_price_hour ck   ────────────   │
│              │             ses_id (FK)          srv_ord_id (PK)│
│              │             srv_date_mod         ord_id (FK)  ──┤
│              │                                   srv_id (FK)  ─┤
│              │                                   ords_hours ck│
│              │                                   ords_total     │
│              │                                   ses_id (FK)    │
│              │                                   ────────────   │
│              │                                   UQ(ord_id,     │
│              │                                     srv_id)      │
└──────────────┴──────────────────────────────────────────────────┘
```

### Convenciones del Modelo

| Elemento | Convención | Ejemplo |
|----------|-----------|---------|
| Nombres de tabla | PascalCase con comillas | `"Orders"`, `"Clients"` |
| Primary Key | `{tabla}_id` | `cli_id`, `ord_id` |
| Foreign Key | mismo nombre que PK referenciada | `cli_id`, `ses_id` |
| Timestamp mod | `{tabla}_date_mod` | `cli_date_mod`, `veh_date_mod` |
| CHECK constraints | `ck_{tabla}_{propiedad}` | `ck_orden_estado` |
| Index compuesto | `idx_{tabla}_{col1}_{col2}` | `idx_ordenes_status_fecha` |
| Index funcional | `idx_{tabla}_upper_{col}` | `idx_vehiculo_upper_plate` |

---

## Endpoints de la API

### Rutas (`/api/v1/...`)

| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| **Auth** ||||
| POST | `/auth/register` | Registrar nuevo usuario | ❌ |
| POST | `/auth/login` | Iniciar sesión → JWT | ❌ |
| GET | `/auth/roles` | Listar roles con bitmask | ❌ |
| GET | `/auth/permisos/{rol}` | Obtener permisos de un rol | ❌ |
| **Clientes** ||||
| GET | `/clients` | Listar clientes | ✅ |
| GET | `/clients/vista/resumen` | Vista `vw_resumen_clientes` | ✅ |
| GET | `/clients/{cli_id}` | Cliente por ID | ✅ |
| POST | `/clients` | Crear cliente | ✅ |
| PATCH | `/clients/{cli_id}` | Actualizar cliente | ✅ |
| DELETE | `/clients/{cli_id}` | Eliminar cliente | ✅ (permiso) |
| **Vehículos** ||||
| GET | `/vehiculos` | Listar vehículos (paginado) | ✅ |
| GET | `/vehiculos/{veh_id}` | Vehículo por ID | ✅ |
| GET | `/vehiculos/cliente/{cli_id}` | Vehículos de un cliente | ✅ |
| POST | `/vehiculos` | Crear vehículo | ✅ |
| PATCH | `/vehiculos/{veh_id}` | Actualizar vehículo | ✅ |
| DELETE | `/vehiculos/{veh_id}` | Eliminar vehículo | ✅ (permiso) |
| **Órdenes** ||||
| GET | `/ordenes` | Listar órdenes | ✅ |
| GET | `/ordenes/vista/activas` | Vista `vw_ordenes_activas` | ✅ |
| GET | `/ordenes/{ord_id}` | Orden por ID | ✅ |
| POST | `/ordenes` | Crear orden con servicios (SAVEPOINT) | ✅ |
| PATCH | `/ordenes/{ord_id}` | Actualizar orden | ✅ |
| DELETE | `/ordenes/{ord_id}` | Eliminar orden + servicios en cascada | ✅ (permiso) |
| PATCH | `/ordenes/{ord_id}/cerrar` | Ejecutar `sp_cerrar_orden` | ✅ (permiso) |
| GET | `/ordenes/{ord_id}/total` | Ejecutar `fn_calcular_total_orden` | ✅ |
| **Servicios** ||||
| GET | `/servicios` | Listar servicios | ✅ |
| GET | `/servicios/{srv_id}` | Servicio por ID | ✅ |
| POST | `/servicios` | Crear servicio | ✅ |
| PATCH | `/servicios/{srv_id}` | Actualizar servicio | ✅ |
| DELETE | `/servicios/{srv_id}` | Eliminar servicio | ✅ (permiso) |
| **IA** ||||
| POST | `/ia/estimar` | Estimar horas vía OpenAI | ✅ |

---

## Autenticación y Permisos

### JWT (HS256 + bcrypt)

```python
# app/auth/jwt.py
def create_access_token(data: dict, expires_delta: timedelta = timedelta(hours=1)):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)
```

### Bitmask Permissions

```python
# app/auth/permissions.py
PERM_VER      = 0x01  # 0001
PERM_CREAR    = 0x02  # 0010
PERM_EDITAR   = 0x04  # 0100
PERM_ELIMINAR = 0x08  # 1000
PERM_ADMIN    = 0xFF  # 11111111
```

### Roles y Máscaras

| Rol | Máscara Hex | Binario | Permisos |
|-----|-------------|---------|----------|
| `admin` | `0xFF` (255) | `11111111` | VER + CREAR + EDITAR + ELIMINAR |
| `mecanico` | `0x07` (7) | `00000111` | VER + CREAR + EDITAR |
| `recepcion` | `0x03` (3) | `00000011` | VER + CREAR |
| `cliente` | `0x01` (1) | `00000001` | VER |

### Validación en cada Endpoint

```python
# app/dependencies.py
def require_permiso(permiso: int):
    def checker(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
        if not tiene_permiso_bd(db, current_user.usr_rol, permiso):
            raise HTTPException(status_code=403, detail="Sin permisos suficientes")
        return current_user
    return checker

# Uso en endpoint protegido:
@router.delete("/{cli_id}")
def delete_cliente(
    cli_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permiso(PERM_ELIMINAR)),
):
    ...
```

---

## Guía de Inicio Rápido

### 1. Entorno Virtual

```bash
cd taller-mecanico-api
python -m venv venv
.\venv\Scripts\Activate.ps1   # Windows PowerShell
pip install -r requirements.txt
```

### 2. Variables de Entorno (`.env`)

```env
DB_USER=taller_app
DB_PASS=TuPasswordSeguro
DB_HOST=adb.us-ashburn-1.oraclecloud.com
DB_PORT=1522
DB_SERVICE=xxxxxxxxxxxxxx_low.adb.oraclecloud.com
DB_DSN=(description=...)

WALLET_LOCATION=wallet
WALLET_PASSWORD=WalletPassword

SECRET_KEY=your-super-secret-key-change-me
PROJECT_NAME="Taller Pro API"
API_V1_STR=/api/v1

OPENAI_API_KEY=sk-...
```

### 3. Wallet Oracle

```bash
# Descargar Wallet desde Oracle Cloud > Autonomous Database > DB Connection
# Extraer en: taller-mecanico-api/wallet/
# Archivos esperados: tnsnames.ora, sqlnet.ora, cwallet.sso, ewallet.p12, etc.

python test_oracle.py   # Verificar conectividad
```

### 4. Migraciones

```bash
alembic upgrade head
```

### 5. Iniciar Servidor

```bash
uvicorn app.main:app --reload --port 8000
```

**URLs:**
- API: `http://localhost:8000/api/v1`
- Swagger Docs: `http://localhost:8000/docs`
- Redoc: `http://localhost:8000/redoc`

---

## Dependencias Principales

| Paquete | Propósito |
|---------|-----------|
| `fastapi` | Framework web asíncrono |
| `uvicorn` | Servidor ASGI |
| `sqlalchemy` ^2.0 | ORM para Oracle |
| `oracledb` | Driver Oracle (thin mode, sin cliente Oracle) |
| `alembic` | Migraciones de base de datos |
| `pydantic` ^2.0 | Validación de datos (schemas) |
| `python-jose` | JWT (HS256) |
| `passlib[bcrypt]` | Hashing de contraseñas |
| `python-multipart` | Soporte para form-data |
| `openai` | Integración GPT-4o-mini |
| `pydantic-settings` | Configuración desde .env |

---

## Resumen de Cumplimiento (Rúbrica Backend)

| Criterio | Estado | Implementación |
|----------|--------|----------------|
| **Arquitectura en Capas** | ✅ | Router → Auth → CRUD → Oracle |
| **Control Transaccional** | ✅ | `db.begin_nested()` (SAVEPOINT) + `sp_cerrar_orden` con COMMIT/ROLLBACK |
| **Manejo ORA-01722** | ✅ | Error handler global + validación Pydantic (`gt=0`, `gt=1900`) |
| **Manejo ORA-02290** | ✅ | Error handler con extracción de constraint name |
| **JWT Auth** | ✅ | HS256 + bcrypt + dependencia `get_current_user` |
| **Bitmask Permissions** | ✅ | `fn_tiene_permiso` en Oracle + `require_permiso` en Python |
| **SAVEPOINT en CRUD** | ✅ | `create_with_services()` con `begin_nested()` |
| **Paginación Genérica** | ✅ | `Pagination[T]` schema + `get_pagination()` en CRUDBase |
| **Logging** | ✅ | Middleware con method/path/status/duration |
| **Error Handlers** | ✅ | ValidationError (422), SQLAlchemyError (500), Exception (500) |
| **CORS Configurado** | ✅ | Múltiples orígenes de desarrollo |
| **Migraciones Alembic** | ✅ | 4 migrations con upgrade/downgrade |

---

<div align="center">
  <sub>FastAPI · Oracle 23ai · SQLAlchemy 2.x · Pydantic v2 · Python 3.12</sub>
</div>

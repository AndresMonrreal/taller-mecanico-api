# opencode.md — Backend (taller-mecanico-api)

> Guía de contexto para el asistente de IA. Léela completa antes de tocar cualquier archivo.

---

## Visión general del proyecto

Sistema de gestión integral para talleres mecánicos. Este paquete es la API REST del sistema.

- **Framework:** FastAPI (Python)
- **Base de datos:** Oracle Autonomous DB (vía SQLAlchemy + `oracledb`)
- **Migraciones:** Alembic
- **Auth:** JWT con permisos bitmask
- **Prefijo global de rutas:** `/api/v1`
- **Runtime:** Python 3.11+

---

## Estructura de carpetas

```
taller-mecanico-api/
├── app/
│   ├── main.py              # Entrada de la app, registro de routers, CORS, middleware
│   ├── core/
│   │   ├── config.py        # Settings via pydantic-settings (lee .env)
│   │   ├── security.py      # Hashing, creación y verificación de JWT
│   │   └── permissions.py   # Constantes bitmask: PERM_VER, PERM_CREAR, etc.
│   ├── db/
│   │   ├── session.py       # Engine SQLAlchemy + get_db dependency
│   │   └── base.py          # Import de todos los modelos (para Alembic)
│   ├── models/              # Modelos SQLAlchemy (una clase por archivo)
│   │   ├── client.py
│   │   ├── vehicle.py
│   │   ├── service.py
│   │   ├── order.py
│   │   ├── service_order.py
│   │   ├── user.py
│   │   └── session.py
│   ├── schemas/             # Pydantic schemas (Request/Response por modelo)
│   ├── routers/             # Un archivo por recurso, registrado en main.py
│   ├── services/            # Lógica de negocio desacoplada del router
│   ├── dependencies/        # FastAPI dependencies reutilizables (get_current_user, etc.)
│   └── migrations/          # Alembic: env.py + versions/
├── tests/
├── .env                     # NO se commitea. Ver .env.example
├── .env.example
├── alembic.ini
└── requirements.txt
```

---

## Convenciones de código

### Nombrado
- Archivos y módulos: `snake_case` (`order_router.py`, `client_service.py`)
- Clases: `PascalCase` (`OrderCreate`, `ClientResponse`)
- Funciones y variables: `snake_case`
- Constantes: `UPPER_SNAKE_CASE` (`PERM_VER = 1`, `PERM_CREAR = 2`)

### Schemas Pydantic
Usa tres schemas por recurso:
```python
class ClientBase(BaseModel): ...       # campos comunes
class ClientCreate(ClientBase): ...    # para POST (sin id, sin timestamps)
class ClientResponse(ClientBase):      # para respuestas
    id: int
    model_config = ConfigDict(from_attributes=True)
```

### Respuestas estándar de la API
Siempre devuelve JSON con esta forma:
```json
{ "data": ..., "message": "ok" }
```
En errores:
```json
{ "detail": "Descripción del error" }
```
Usa `HTTPException` de FastAPI. No uses respuestas planas sin estructura.

---

## Base de datos

- **Driver:** `oracledb` en modo thin (no requiere Oracle Client instalado)
- **ORM:** SQLAlchemy 2.x con sintaxis declarativa moderna
- **Nunca** uses SQL crudo directo. Usa el ORM o `text()` solo cuando sea estrictamente necesario
- Los nombres de tablas y columnas en Oracle van en **MAYÚSCULAS** por convención:
  ```python
  __tablename__ = "CLIENTS"
  id = Column("CLIENT_ID", Integer, primary_key=True)
  ```
- Toda migración va por **Alembic**. No alteres la BD manualmente en producción.

### Manejo de sesión
```python
# Siempre usa la dependency, nunca crees sesiones manualmente en routers
def get_client(client_id: int, db: Session = Depends(get_db)): ...
```

---

## Autenticación y permisos

> Auth con JWT está planificado pero aún no implementado. Cuando lo hagas, sigue este patrón:

### JWT
- Access token de corta duración (15–60 min)
- Refresh token en cookie `httpOnly` (7 días)
- Payload mínimo: `{ "sub": user_id, "permissions": bitmask, "exp": ... }`

### Permisos bitmask
```python
# app/core/permissions.py
PERM_VER    = 1   # 0001
PERM_CREAR  = 2   # 0010
PERM_EDITAR = 4   # 0100
PERM_BORRAR = 8   # 1000

# Verificación
def has_permission(user_perms: int, required: int) -> bool:
    return (user_perms & required) == required
```

### Dependency de usuario actual (cuando se implemente)
```python
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    ...
```

---

## Routers

- Un archivo por recurso en `app/routers/`
- Registrados en `main.py` con prefijo `/api/v1`:
  ```python
  app.include_router(clients.router, prefix="/api/v1/clients", tags=["clients"])
  ```
- El router solo orquesta: valida input, llama al service, devuelve respuesta
- **No pongas lógica de negocio en el router**

---

## Servicios (capa de negocio)

- Toda lógica que no sea "recibir request / devolver response" va en `app/services/`
- Los servicios reciben la sesión de BD como argumento, no la crean
- Ejemplo:
  ```python
  # app/services/client_service.py
  def create_client(db: Session, data: ClientCreate) -> Client:
      client = Client(**data.model_dump())
      db.add(client)
      db.commit()
      db.refresh(client)
      return client
  ```

---

## Manejo de errores

- Usa siempre `HTTPException` con status codes correctos:
  - `404` → recurso no encontrado
  - `400` → datos inválidos o regla de negocio violada
  - `401` → no autenticado
  - `403` → sin permisos
  - `409` → conflicto (ej. duplicado)
  - `500` → error inesperado (loggea antes de lanzar)
- **No** uses `print()` para debug en producción. Usa `logging` del stdlib de Python.
- Maneja excepciones de SQLAlchemy en el service, no en el router.

---

## Variables de entorno

Nunca hardcodees valores de conexión o secrets en el código. Todo va en `.env`:

```env
# .env.example
DATABASE_URL=oracle+oracledb://user:pass@host:1521/?service_name=nombre
SECRET_KEY=cambia_esto_en_produccion
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

- Léelas con `pydantic-settings` en `app/core/config.py`
- `.env` está en `.gitignore`. **Nunca lo commitees.**
- `.env.example` sí se commitea, con valores de placeholder.

---

## Testing

- Framework: `pytest` + `httpx` (cliente async para FastAPI)
- Tests en `tests/`, espejando la estructura de `app/`
- Usa una BD de test separada o mocks de sesión
- Mínimo: un test por endpoint por método HTTP
- Convención de nombres: `test_<acción>_<recurso>_<escenario>`
  ```
  test_create_client_success
  test_create_client_missing_fields
  test_get_client_not_found
  ```

---

## Git

- Rama principal: `main`
- Convención de commits: **Conventional Commits**
  ```
  feat(clients): agregar endpoint de creación
  fix(auth): corregir validación de token expirado
  chore(deps): actualizar fastapi a 0.111
  refactor(orders): mover lógica a service layer
  ```
- No hacer push directo a `main`. Usa ramas de feature: `feat/nombre-feature`
- Un PR por feature o fix

---

## Lo que NO debes hacer

- ❌ No pongas lógica en los routers, solo en services
- ❌ No uses SQL crudo sin pasar por ORM o `text()`
- ❌ No commitees `.env` ni credenciales
- ❌ No modifiques la BD directamente en producción; siempre usa Alembic
- ❌ No uses `print()` en código de producción
- ❌ No devuelvas respuestas sin estructura consistente
- ❌ No crees sesiones de BD fuera del sistema de dependencies

---

## Estado actual del proyecto (referencia rápida)

| Área | Estado |
|------|--------|
| Modelos | Definidos: Client, Vehicle, Service, Order, ServiceOrder, User, Session |
| Migraciones | Alembic configurado |
| Auth / JWT | Planificado, no implementado |
| Permisos bitmask | Diseñados, pendiente de integrar |
| Tests | Por implementar |
| Deploy | Pendiente de definir |
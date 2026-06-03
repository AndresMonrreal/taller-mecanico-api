from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings
from app.core.errors import validation_exception_handler, sqlalchemy_exception_handler, generic_exception_handler
from app.middleware.logging_middleware import log_requests

from app.routers import clientes, vehiculos, ordenes, servicios, auth, ia

# Instancia principal de la aplicación FastAPI
app = FastAPI(title=settings.PROJECT_NAME)

# Configuración de CORS: permite peticiones desde los frontends en desarrollo
app.add_middleware(CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:8080",
        "http://localhost:8000",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8080",
        "http://127.0.0.1:8000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Middleware personalizado para logging de requests
app.add_middleware(BaseHTTPMiddleware, dispatch=log_requests)

# Manejadores globales de excepciones
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Registro de todos los routers bajo el prefijo /api/v1
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(clientes.router, prefix=settings.API_V1_STR)
app.include_router(vehiculos.router, prefix=settings.API_V1_STR)
app.include_router(ordenes.router, prefix=settings.API_V1_STR)
app.include_router(servicios.router, prefix=settings.API_V1_STR)
app.include_router(ia.router, prefix=settings.API_V1_STR)


@app.get("/")
def root():
    """Endpoint raíz de verificación de estado del servidor."""
    return {"message": f"{settings.PROJECT_NAME} corriendo"}
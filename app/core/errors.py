from fastapi import HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError


async def validation_exception_handler(request, exc):
    """
    Maneja errores de validación de Pydantic/FastAPI (HTTP 422).
    Retorna los detalles del error de validación en la respuesta.
    """
    return JSONResponse(status_code=422, content={"detail": exc.errors(), "message": "Error de Validacion"})


async def sqlalchemy_exception_handler(request, exc):
    """
    Maneja excepciones de SQLAlchemy (HTTP 500).
    Captura errores de base de datos y los retorna como respuesta JSON.
    """
    return JSONResponse(status_code=500, content={"message": "Error de Base de Datos", "detail": str(exc)})


async def generic_exception_handler(request, exc):
    """
    Maneja cualquier excepción no capturada (HTTP 500).
    Retorna un mensaje genérico sin exponer detalles internos.
    """
    return JSONResponse(status_code=500, content={"message": "Error interno del Servidor"})


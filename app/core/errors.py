from fastapi import HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError

async def validation_exception_handler(request, exc):
    return JSONResponse(status_code = 422, content={"detail":exc.errors(), "message":"Error de Validacion"})

async def sqlalchemy_exception_handler(request, exc):
    return JSONResponse(status_code = 500, content = {"message" : "Error de Base de Datos","detail": str(exc)})

async def generic_exception_handler(request, exc):
    return JSONResponse(status_code = 500, content = {"message" : "Error interno del Servidor"})


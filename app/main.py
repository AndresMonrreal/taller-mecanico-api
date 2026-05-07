from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings
from app.core.errors import validation_exception_handler, sqlalchemy_exception_handler, generic_exception_handler
from app.middleware.logging_middleware import log_requests


app = FastAPI(title = settings.PROJECT_NAME)
# CORS para que React pueda conectarse
app.add_middleware(CORSMiddleware, allow_origins = ["http://localhost:5173"], allow_methods = ["*"], allow_headers = ["*"])

#Logging
app.add_middleware(BaseHTTPMiddleware, dispatch = log_requests)

#Errores globales

app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

@app.get("/")
def root():
    return {"message":f"{settings.PROJECT_NAME} corriendo"}
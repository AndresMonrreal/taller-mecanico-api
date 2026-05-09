from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings
from app.core.errors import validation_exception_handler, sqlalchemy_exception_handler, generic_exception_handler
from app.middleware.logging_middleware import log_requests

from app.routers import clientes, vehiculos, ordenes, servicios, auth, ia

app = FastAPI(title=settings.PROJECT_NAME, root_path=settings.API_V1_STR)

app.add_middleware(CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.add_middleware(BaseHTTPMiddleware, dispatch=log_requests)

app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

app.include_router(auth.router)
app.include_router(clientes.router)
app.include_router(vehiculos.router)
app.include_router(ordenes.router)
app.include_router(servicios.router)
app.include_router(ia.router)

@app.get("/")
def root():
    return {"message": f"{settings.PROJECT_NAME} corriendo"}
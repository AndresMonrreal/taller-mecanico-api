from pydantic import BaseModel
from typing import TypeVar, Generic, List

# Tipo genérico para los datos paginados
T = TypeVar('T')


class Pagination(BaseModel, Generic[T]):
    """
    Schema genérico para respuestas paginadas.
    Se usa con cualquier tipo de dato mediante el parámetro genérico T.
    """
    total: int       # Total de registros disponibles
    page: int        # Página actual
    size: int        # Cantidad de registros por página
    pages: int       # Total de páginas calculado
    data: list[T]    # Lista de elementos de la página actual
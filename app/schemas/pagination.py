from pydantic import BaseModel
from typing import TypeVar, Generic, List

T = TypeVar('T')

class Pagination(BaseModel, Generic[T]):
    total:int 
    page:int
    size:int
    pages:int
    data: list[T]
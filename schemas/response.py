from pydantic import BaseModel, Field
from typing import Optional, Any, TypeVar, Generic, List

T = TypeVar('T')

class StandardResponse(BaseModel):
    status: str = Field(default="success")
    message: str = Field(..., description="Message")
    data: Optional[Any] = None

class ErrorResponse(BaseModel):
    status: str = Field(default="error")
    message: str = Field(..., description="Message about error")
    status_code: int = Field(..., description="HTTP status code")
    detail: str = Field(..., description="Detail about error")

class PaginatedResponse(BaseModel, Generic[T]):
    """Ответ с пагинацией"""
    items: List[T]
    total: int
    page: int
    per_page: int
    pages: int
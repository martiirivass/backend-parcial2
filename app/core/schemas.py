import math
from typing import Generic, List, TypeVar
from sqlmodel import SQLModel

T = TypeVar("T")


class PaginatedResponse(SQLModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    size: int
    pages: int

    @classmethod
    def create(
        cls, items: List[T], total: int, page: int, size: int
    ) -> "PaginatedResponse[T]":
        return cls(
            items=items,
            total=total,
            page=page,
            size=size,
            pages=math.ceil(total / size) if size > 0 else 0,
        )

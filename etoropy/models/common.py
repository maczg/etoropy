from __future__ import annotations

from pydantic import BaseModel


class PaginatedRequest(BaseModel):
    page: int | None = None
    page_size: int | None = None


class PaginatedResponse(BaseModel):
    page: int
    page_size: int = 0
    total_items: int = 0

    model_config = {"populate_by_name": True}


class TokenResponse(BaseModel):
    token: str

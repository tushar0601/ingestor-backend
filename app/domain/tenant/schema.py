from uuid import UUID
from datetime import datetime
from typing import List
from pydantic import BaseModel, Field, ConfigDict

class TenantResponse(BaseModel):
    id: UUID
    name: str
    max_file_size_mb: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class TenantListResponse(BaseModel):
    items: List[TenantResponse]
    total: int

class TenantCreate(BaseModel):
    name: str = Field(
        ...,
        min_length=2,
        max_length=255,
    )

    api_key: str = Field(
        ...,
        min_length=32,
        max_length=128,
    )

    max_file_size_mb: int = Field(
        default=100,
        ge=1,
        le=10_000,
        description="Maximum allowed file size per upload (in MB)",
    )

    model_config = ConfigDict(extra="forbid")
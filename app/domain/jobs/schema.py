from uuid import UUID
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field, ConfigDict


class JobCreate(BaseModel):
    tenant_id: UUID
    file_id: UUID

    job_type: str = Field(
        min_length=1,
        max_length=64,
        description="e.g. PROCESS_FILE",
    )

    status: str = Field(
        default="PENDING",
        min_length=1,
        max_length=16,
        description="PENDING | RUNNING | SUCCEEDED | FAILED",
    )

    error_message: Optional[str] = Field(
        default=None,
        max_length=2000,
    )

    model_config = ConfigDict(extra="forbid")


class JobResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    file_id: UUID

    job_type: str
    status: str
    error_message: Optional[str]

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class JobListResponse(BaseModel):
    items: List[JobResponse]
    total: int

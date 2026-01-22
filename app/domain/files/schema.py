from __future__ import annotations

from datetime import datetime
from typing import Dict, Optional, List
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field
from app.domain.jobs.schema import JobResponse

class FileCreate(BaseModel):
    original_filename: str
    tenant_id: UUID
    content_type: str
    size_bytes: int
    storage_path: str
    status: str = Field(default="UPLOADED")
    upload_mode: str = Field(default="DIRECT")
    file_metadata: Optional[Dict] = None

    model_config = ConfigDict(extra="forbid")


class FileResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    original_filename: str
    content_type: str
    size_bytes: int
    storage_path: str
    status: str
    upload_mode: str
    file_metadata: Optional[Dict]
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class FileListResponse(BaseModel):
    items: List[FileResponse]
    total: int

class UploadResponse(BaseModel):
    file: FileResponse
    job: JobResponse
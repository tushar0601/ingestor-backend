from pydantic import BaseModel, Field, conint
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from typing_extensions import Annotated

class UploadInitiateIn(BaseModel):
    filename: str
    content_type: Optional[str]
    size_bytes: int

class UploadInitiateOut(BaseModel):
    upload_id: UUID
    bucket: str
    key: str
    part_size_bytes: int
    expires_at: datetime

class PresignPartIn(BaseModel):
    part_number: Annotated[int, Field(ge=1, le=10_000)]

class UploadPartOut(BaseModel):
    part_number: int
    etag: str
    size: Optional[int] = None

class UploadPartsOut(BaseModel):
    parts: List[UploadPartOut]

class CompletePartIn(BaseModel):
    part_number: Annotated[int, Field(ge=1, le=10_000)]
    etag: str

class CompleteUploadIn(BaseModel):
    parts: List[CompletePartIn] = Field(..., min_length=1)

class CompleteUploadOut(BaseModel):
    status: str
    bucket: str
    key: str
    size_bytes: int

class UploadStatusOut(BaseModel):
    upload_id: UUID
    status: str
    filename: str
    content_type: Optional[str] = None
    size_bytes_expected: int
    bucket: str
    key: str
    created_at: datetime
    expires_at: datetime
    uploaded_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    processing_job_id: Optional[UUID] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None

class PresignPartOut(BaseModel):
    signed_url: str
    expires_in: int
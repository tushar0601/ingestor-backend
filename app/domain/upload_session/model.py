import enum
import uuid
from datetime import datetime, timedelta
from sqlalchemy import (
    Column,
    String,
    DateTime,
    BigInteger,
    Enum,
    Text,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.core.db import Base

class UploadStatus(str, enum.Enum):
    PENDING_UPLOAD = "PENDING_UPLOAD"
    UPLOADED = "UPLOADED"
    PROCESSING = "PROCESSING"
    PROCESSED = "PROCESSED"
    FAILED = "FAILED"
    EXPIRED = "EXPIRED"
    ABORTED = "ABORTED"


class UploadSession(Base):
    __tablename__ = "upload_sessions"
    __table_args__ = (
        Index("ix_upload_sessions_tenant_id_created_at", "tenant_id", "created_at"),
        Index("ix_upload_sessions_status_expires_at", "status", "expires_at"),
        Index(
            "ix_upload_sessions_tenant_idempotency_key",
            "tenant_id",
            "idempotency_key",
            unique=True,
        ),
        Index(
            "ix_upload_sessions_bucket_object_key",
            "bucket",
            "object_key",
            unique=True,
        ),
        {"schema": "jobs"},
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID, nullable=False)
    filename = Column(String, nullable=False)
    content_type = Column(String, nullable=True)
    size_bytes_expected = Column(BigInteger, nullable=False)
    bucket = Column(String, nullable=False)
    object_key = Column(String, nullable=False)
    storage_upload_id = Column(String, nullable=False)
    part_size_bytes = Column(BigInteger, nullable=False)
    status = Column(String, nullable=False)
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    expires_at = Column(DateTime(timezone=True), nullable=False)
    uploaded_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    processing_job_id = Column(UUID(as_uuid=True), nullable=True)
    error_code = Column(String, nullable=True)
    error_message = Column(Text, nullable=True)
    idempotency_key = Column(String, nullable=True)

    @staticmethod
    def default_expires_at(hours: int = 24) -> datetime:
        return datetime.utcnow() + timedelta(hours=hours)

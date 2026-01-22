from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Integer, String, func, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base

class FileObject(Base):
    __tablename__ = "file_object"
    __table_args__ = {"schema": "file"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenant.tenant_object.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    original_filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    content_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        doc="MIME type, e.g. application/pdf, image/png",
    )

    size_bytes: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    storage_path: Mapped[str] = mapped_column(
        String(1024),
        nullable=False,
        doc="Object storage key/path, e.g. tenant-<id>/raw/<file_id>",
    )

    status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        index=True,
        doc="PENDING_UPLOAD | UPLOADED | PROCESSING | PROCESSED | FAILED",
    )

    upload_mode: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        index=True,
        doc="DIRECT | FORM",
    )

    file_metadata: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
        doc="Type-specific extracted metadata and processed artifact references",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
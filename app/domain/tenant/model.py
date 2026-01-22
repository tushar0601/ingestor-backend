from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class Tenant(Base):
    __tablename__ = "tenant_object"
    __table_args__ = {"schema": "tenant"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        index=True,
    )

    api_key_hash: Mapped[str] = mapped_column(
        String(256),
        nullable=False,
        unique=True,
        index=True,
        doc="SHA-256 (or HMAC) hash of the tenant API key",
    )

    max_file_size_mb: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=100,
        doc="Maximum allowed file size per upload (in MB)",
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

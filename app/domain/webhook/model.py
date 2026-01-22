from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class Webhook(Base):
    __tablename__ = "webhook_object"
    __table_args__ = {"schema": "webhook"}

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

    url: Mapped[str] = mapped_column(
        String(2048),
        nullable=False,
        doc="Webhook callback URL",
    )

    secret: Mapped[str] = mapped_column(
        String(512),
        nullable=False,
        doc="Signing secret for webhook payloads (store hashed later if desired)",
    )

    event_types: Mapped[list[str]] = mapped_column(
        JSONB,
        nullable=False,
        doc='JSON array of event types, e.g. ["file.processed"]',
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

import os
import re
from uuid import uuid4, UUID
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from typing import List, Dict

from app.core.config import settings
from app.core.constants import (
    DEFAULT_PART_SIZE_BYTES,
    DEFAULT_PRESIGN_TTL_SECONDS,
    DEFAULT_UPLOAD_TTL_HOURS,
)
from app.domain.upload_session.model import UploadSession, UploadStatus
from app.repository.upload_repository import UploadSessionRepository
from app.services.service_utils import assert_transition
from app.services.storage_service import StorageService


_SAFE_NAME_RE = re.compile(r"[^a-zA-Z0-9._-]+")


def sanitize_filename(name: str) -> str:
    base = os.path.basename(name).strip()
    base = _SAFE_NAME_RE.sub("_", base)
    return base[:200] if base else "file"


def build_object_key(tenant_id: UUID, upload_id: UUID, filename: str) -> str:
    safe = sanitize_filename(filename)
    return f"tenant/{tenant_id}/uploads/{upload_id}/{safe}"


class UploadService:

    def __init__(self, db: Session):
        self.repo = UploadSessionRepository(db=db)
        self.storage_service = StorageService()

    def initiate(
        self,
        tenant_id: UUID,
        filename: str,
        content_type: str | None,
        size_bytes: int,
        idempotency_key: str | None = None,
        part_size_bytes: int = DEFAULT_PART_SIZE_BYTES,
        ttl_hours: int = DEFAULT_UPLOAD_TTL_HOURS,
    ) -> UploadSession:
        max_bytes = settings.MAX_UPLOAD_BYTES
        if max_bytes and size_bytes > max_bytes:
            raise ValueError(f"File too large: {size_bytes} > {max_bytes}")

        parts_needed = (size_bytes + part_size_bytes - 1) // part_size_bytes
        if parts_needed > 10_000:
            raise ValueError("Too many parts; increase part_size_bytes.")

        upload_id = uuid4()
        bucket = settings.S3_BUCKET
        key = build_object_key(
            tenant_id=tenant_id, upload_id=upload_id, filename=filename
        )

        storage_upload_id = self.storage_service.initiate_multipart(
            bucket=bucket, key=key, content_type=content_type
        )

        expires_at = datetime.utcnow() + timedelta(hours=ttl_hours)

        session = UploadSession(
            id=upload_id,
            tenant_id=tenant_id,
            filename=filename,
            content_type=content_type,
            size_bytes_expected=size_bytes,
            bucket=bucket,
            object_key=key,
            storage_upload_id=storage_upload_id,
            part_size_bytes=part_size_bytes,
            status=UploadStatus.PENDING_UPLOAD.value,
            expires_at=expires_at,
            idempotency_key=idempotency_key,
        )

        return self.repo.create(session=session)

    def presign_part(
        self,
        upload_id: UUID,
        part_number: int,
        expires_in: int = DEFAULT_PRESIGN_TTL_SECONDS,
    ) -> str:

        session = self._must_get(upload_id=upload_id)

        if session.status != UploadStatus.PENDING_UPLOAD.value:
            raise ValueError(f"Cannot presign part in status={session.status}")

        if session.expires_at and datetime.utcnow() > session.expires_at.replace(
            tzinfo=None
        ):
            raise ValueError("Upload session expired.")

        return self.storage_service.presign_part_upload(
            bucket=session.bucket,
            key=session.object_key,
            storage_upload_id=session.storage_upload_id,
            part_number=part_number,
            expires_in=expires_in,
        )

    def list_parts(self, upload_id: UUID) -> List[Dict]:
        session = self._must_get(upload_id=upload_id)

        if session.status not in {
            UploadStatus.PENDING_UPLOAD.value,
            UploadStatus.UPLOADED.value,
        }:
            pass

        return self.storage_service.list_parts(
            bucket=session.bucket,
            key=session.object_key,
            storage_upload_id=session.storage_upload_id,
        )

    def complete(self, upload_id: UUID, parts: List[Dict]) -> UploadSession:
        session = self._must_get(upload_id=upload_id)

        if session.status != UploadStatus.PENDING_UPLOAD.value:

            if session.status == UploadStatus.UPLOADED.value:
                return session
            raise ValueError(f"Cannot complete upload in status={session.status}")

        self.storage_service.complete_multipart(
            bucket=session.bucket,
            key=session.object_key,
            storage_upload_id=session.storage_upload_id,
            parts=parts,
        )

        head = self.storage_service.head_object(
            bucket=session.bucket, key=session.object_key
        )
        size = int(head["ContentLength"])

        if size != int(session.size_bytes_expected):
            session.status = UploadStatus.FAILED.value
            session.error_code = "SIZE_MISMATCH"
            session.error_message = (
                f"Expected {session.size_bytes_expected}, got {size}"
            )
            session.completed_at = datetime.utcnow()
            return self.repo.update(session=session)

        assert_transition(session.status, UploadStatus.UPLOADED.value)
        session.status = UploadStatus.UPLOADED.value
        session.uploaded_at = datetime.utcnow()
        session.completed_at = datetime.utcnow()

        # PLUG: enqueue your existing job here
        # job_id = enqueue_processing_job(...)
        # session.processing_job_id = job_id

        return self.repo.update(session)

    def abort(self, upload_id: UUID) -> UploadSession:
        session = self._must_get(upload_id)

        if session.status in {UploadStatus.ABORTED.value, UploadStatus.EXPIRED.value}:
            return session

        if session.status not in {UploadStatus.PENDING_UPLOAD.value}:
            raise ValueError(f"Cannot abort in status={session.status}")

        self.storage_service.abort_multipart(
            bucket=session.bucket,
            key=session.object_key,
            storage_upload_id=session.storage_upload_id,
        )

        assert_transition(session.status, UploadStatus.ABORTED.value)
        session.status = UploadStatus.ABORTED.value
        session.completed_at = datetime.utcnow()
        return self.repo.update(session)

    def get_status(self, upload_id: UUID) -> UploadSession:
        return self._must_get(upload_id)

    def _must_get(self, upload_id: UUID) -> UploadSession:
        session = self.repo.get(upload_id)
        if not session:
            raise ValueError("Upload session not found.")
        return session

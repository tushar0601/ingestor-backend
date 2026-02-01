from __future__ import annotations
from typing import Any, Dict, Tuple
from datetime import datetime, timezone

from app.domain.files.model import FileObject
from app.services.storage_service import StorageService
from app.processors.errors import NonRetryableProcessingError

from app.processors.csv_processor import CSVProcessor
from app.processors.image_processor import ImageProcessor
from app.processors.pdf_processor import PDFProcessor


def _normalize_content_type(content_type: str | None) -> str:
    if not content_type:
        return ""
    return content_type.split(";")[0].strip().lower()


def build_metadata_envelope(
    processor: str, version: int, data: Dict[str, Any]
) -> Dict[str, Any]:
    return {
        "processor": processor,
        "version": version,
        "extracted_at": datetime.now(timezone.utc).isoformat(),
        "data": data,
    }


def process_file(
    file_obj: FileObject, storage_service: StorageService
) -> Tuple[Dict[str, Any], int]:
    """
    Entry point for workers.

    Returns:
      (metadata_dict, processing_version)
    """
    ct = _normalize_content_type(getattr(file_obj, "content_type", None))

    if ct in ("text/csv", "application/csv", "application/vnd.ms-excel"):
        p = CSVProcessor()
        data = p.process(file_obj, storage_service)
        meta = build_metadata_envelope(processor="csv", version=p.version, data=data)
        return meta, p.version

    if ct in (
        "image/png",
        "image/jpeg",
        "image/jpg",
        "image/webp",
        "image/gif",
        "image/tiff",
    ):
        p = ImageProcessor()
        data = p.process(file_obj, storage_service)
        meta = build_metadata_envelope(processor="image", version=p.version, data=data)
        return meta, p.version

    if ct in ("application/pdf",):
        p = PDFProcessor()
        data = p.process(file_obj, storage_service)
        meta = build_metadata_envelope(processor="pdf", version=p.version, data=data)
        return meta, p.version

    raise NonRetryableProcessingError(f"Unsupported content_type={ct or 'unknown'}")

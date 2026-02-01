from __future__ import annotations

import io
from typing import Any, Dict

from pypdf import PdfReader

from app.domain.files.model import FileObject
from app.services.storage_service import StorageService
from app.processors.errors import NonRetryableProcessingError


class PDFProcessor:

    def __init__(self):
        self.kind = "pdf"
        self.version = 1

    def process(
        self, file_obj: FileObject, storage_service: StorageService
    ) -> Dict[str, Any]:
        raw = storage_service.download_bytes(
            file_obj.storage_path, max_bytes=25 * 1024 * 1024
        )

        try:
            reader = PdfReader(io.BytesIO(raw))
            page_count = len(reader.pages)
        except Exception:
            raise NonRetryableProcessingError("Unsupported/corrupt PDF")

        return {
            "kind": self.kind,
            "version": self.version,
            "page_count": page_count,
        }

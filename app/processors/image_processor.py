from __future__ import annotations

import io
from typing import Any, Dict

from PIL import Image, UnidentifiedImageError

from app.domain.files.model import FileObject
from app.services.storage_service import StorageService
from app.processors.errors import NonRetryableProcessingError


class ImageProcessor:

    def __init__(self):
        self.kind = "image"
        self.version = 1

    def process(
        self, file_obj: FileObject, storage_service: StorageService
    ) -> Dict[str, Any]:

        raw = storage_service.download_bytes(
            storage_path=file_obj.storage_path, max_bytes=10 * 1024 * 1024
        )

        try:
            with Image.open(io.BytesIO(raw)) as img:
                width, height = img.size
                fmt = (img.format or "").upper() or "UNKNOWN"
        except UnidentifiedImageError:
            raise NonRetryableProcessingError("Unsupported/corrupt image")
        except Exception as e:
            # For Phase 2, keep unexpected errors as non-retryable only if clearly file-related.
            raise

        return {
            "kind": self.kind,
            "version": self.version,
            "format": fmt,
            "width": width,
            "height": height,
        }

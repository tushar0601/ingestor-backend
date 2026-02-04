from __future__ import annotations

import csv
import io
from typing import Any, Dict, List

from app.domain.files.model import FileObject
from app.services.storage_service import StorageService
from app.processors.errors import NonRetryableProcessingError


class CSVProcessor:

    def __init__(self):
        self.kind = "csv"
        self.version = 1

    def process(
        self, file_obj: FileObject, storage_service: StorageService
    ) -> Dict[str, Any]:

        raw = storage_service.download_bytes(
            file_obj.storage_path, max_bytes=5 * 1024 * 1024
        )

        try:
            text = raw.decode("utf-8")
            encoding = "utf-8"
        except UnicodeDecodeError:
            text = raw.decode("latin-1")
            encoding = "latin-1"

        sample = text[:4096]
        try:
            dialect = csv.Sniffer().sniff(sample, delimiters=[",", "\t", ";", "|"])
            delimiter = dialect.delimiter
        except Exception:
            delimiter = ","

        reader = csv.reader(io.StringIO(text), delimiter=delimiter)

        try:
            header = next(reader)
        except StopIteration:
            raise NonRetryableProcessingError("Empty CSV file")

        row_count = 0
        for _ in reader:
            row_count += 1

        columns: List[str] = [c.strip() for c in header if c is not None]

        return {
            "kind": self.kind,
            "version": self.version,
            "encoding": encoding,
            "delimiter": delimiter,
            "columns": columns,
            "row_count": row_count,
        }

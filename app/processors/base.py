from __future__ import annotations
from typing import Protocol, Tuple, Dict, Any

from app.domain.files.model import FileObject
from app.services.storage_service import StorageService

class FileProcessor(Protocol):

    kind: str
    version: int

    def process(self,file_obj:FileObject, storage: StorageService) -> Dict[str,Any]:
        ...
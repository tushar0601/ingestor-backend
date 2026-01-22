from fastapi import Depends
from sqlalchemy.orm import Session

from app.services.storage_service import StorageService
from app.core.db import get_db


def get_storage_service(db: Session = Depends(get_db)) -> StorageService:
    return StorageService()

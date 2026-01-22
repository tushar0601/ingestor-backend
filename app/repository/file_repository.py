from typing import List, Optional
import uuid
from sqlalchemy.orm import Session
from app.domain.files.model import FileObject


class FileRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all_files(self) -> List[FileObject]:
        return self.db.query(FileObject).all()

    def create_file(self, data: FileObject) -> FileObject:
        self.db.add(data)
        self.db.commit()
        self.db.refresh(data)
        return data

    def get_file_by_id(
        self, tenant_id: uuid.UUID, file_id: uuid.UUID
    ) -> Optional[FileObject]:
        return (
            self.db.query(FileObject)
            .filter(FileObject.id == file_id, FileObject.tenant_id == tenant_id)
            .first()
        )

    def list_files(
            self,
            tenant_id: uuid.UUID,
            skip:int,
            limit:int,
            status: str | None = None,
            filename_contains: str | None = None
    ) -> List[FileObject]:
        query = self.db.query(FileObject).filter(FileObject.tenant_id == tenant_id)

        if status:
            query = query.filter(FileObject.status == status)
        
        if filename_contains:
            query = query.filter(FileObject.original_filename.ilike(f"%{filename_contains}%"))
        
        return query.order_by(FileObject.created_at.desc()).offset(skip).limit(limit).all()
    
    def count_files(
            self,
            tenant_id: uuid.UUID,
            status: str | None = None,
            filename_contains: str | None = None,
    ) -> int:
        query = self.db.query(FileObject).filter(FileObject.tenant_id == tenant_id)

        if status:
            query = query.filter(FileObject.status == status)
        
        if filename_contains:
            query = query.filter(FileObject.original_filename.ilike(f"%{filename_contains}%"))

        return query.count()
import uuid
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repository.file_repository import FileRepository
from app.domain.files.schema import FileCreate, FileResponse, FileListResponse
from app.domain.files.model import FileObject


class FileService:
    def __init__(self, db: Session):
        self.repo = FileRepository(db=db)

    def create_file(self, file_id: uuid.UUID, payload: FileCreate) -> FileResponse:
        data = FileObject(
            id=file_id,
            tenant_id=payload.tenant_id,
            original_filename=payload.original_filename,
            content_type=payload.content_type,
            size_bytes=payload.size_bytes,
            storage_path=payload.storage_path,
            status=payload.status,
            upload_mode=payload.upload_mode,
            file_metadata=payload.file_metadata,
        )
        result = self.repo.create_file(data=data)
        return FileResponse.model_validate(result)

    def get_file(self, tenant_id: uuid.UUID, file_id: uuid.UUID) -> FileResponse:
        obj = self.repo.get_file_by_id(tenant_id=tenant_id, file_id=file_id)
        if not obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="File not found"
            )

        return FileResponse.model_validate(obj)

    def list_files(
        self,
        tenant_id: uuid.UUID,
        skip: int,
        limit: int,
        status: str | None = None,
        filename_contains: str | None = None,
    ) -> FileListResponse:
        items = self.repo.list_files(
            tenant_id=tenant_id,
            skip=skip,
            limit=limit,
            status=status,
            filename_contains=filename_contains,
        )
        total = self.repo.count_files(
            tenant_id=tenant_id, status=status, filename_contains=filename_contains
        )

        return FileListResponse(
            items=[FileResponse.model_validate(item) for item in items], total=total
        )

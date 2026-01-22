import uuid
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status, Query
from fastapi.responses import StreamingResponse
from urllib.parse import quote

from app.dependencies.tenant_dependency import get_current_tenant
from app.dependencies.file_dependency import get_file_service
from app.dependencies.jobs_dependency import get_job_service
from app.domain.tenant.model import Tenant
from app.domain.files.schema import (
    FileCreate,
    FileResponse,
    FileListResponse,
    UploadResponse,
)
from app.domain.jobs.schema import JobCreate
from app.services.file_service import FileService
from app.services.storage_service import StorageService
from app.services.jobs_service import JobService

router = APIRouter()


@router.post(
    "/upload", response_model=UploadResponse, status_code=status.HTTP_201_CREATED
)
async def upload_file(
    file: UploadFile = File(...),
    current_tenant: Tenant = Depends(get_current_tenant),
    file_service: FileService = Depends(get_file_service),
    job_service: JobService = Depends(get_job_service),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="filename is required")

    file_id = uuid.uuid4()
    storage_path = f"tenant-{current_tenant.id}/raw/{file_id}/{file.filename}"
    content_type = file.content_type or "application/octet-stream"

    storage = StorageService()

    try:
        result = storage.upload_fileobj(
            fileobj=file.file,
            key=storage_path,
            content_type=content_type,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"upload failed: {str(e)}")

    payload = FileCreate(
        tenant_id=current_tenant.id,
        original_filename=file.filename,
        content_type=content_type,
        size_bytes=result.size_bytes,
        storage_path=storage_path,
        status="UPLOADED",
        upload_mode="DIRECT",
        file_metadata=None,
    )

    try:
        created_file = file_service.create_file(file_id=file_id, payload=payload)
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to create file entry in DB")

    job_payload = JobCreate(
        tenant_id=current_tenant.id,
        file_id=file_id,
        job_type="PENDING",
    )

    try:
        created_job = job_service.create_job(payload=job_payload)
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to create job entry in DB")

    return UploadResponse(file=created_file, job=created_job)


@router.get("/{file_id}", response_model=FileResponse)
def get_file_metadata(
    file_id: uuid.UUID,
    current_tenant: Tenant = Depends(get_current_tenant),
    file_service: FileService = Depends(get_file_service),
):
    return file_service.get_file(tenant_id=current_tenant.id, file_id=file_id)


@router.get("/", response_model=FileListResponse)
def list_files(
    current_tenant: Tenant = Depends(get_current_tenant),
    file_service: FileService = Depends(get_file_service),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=200),
    status: str | None = Query(None),
    filename_contains: str | None = Query(None),
):
    return file_service.list_files(
        tenant_id=current_tenant.id,
        skip=skip,
        limit=limit,
        status=status,
        filename_contains=filename_contains,
    )


@router.get("/{file_id}/download")
def download_file(
    file_id: uuid.UUID,
    current_tenant: Tenant = Depends(get_current_tenant),
    file_service: FileService = Depends(get_file_service),
):
    meta = file_service.get_file(tenant_id=current_tenant.id, file_id=file_id)

    storage_service = StorageService()
    obj = storage_service.get_object(key=meta.storage_path)
    body = obj["Body"]

    filename = meta.original_filename
    quoted = quote(filename)

    return StreamingResponse(
        body.iter_chunks(chunk_size=1024 * 1024),
        media_type=meta.content_type,
        headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{quoted}",
        },
    )

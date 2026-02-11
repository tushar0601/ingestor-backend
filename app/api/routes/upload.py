from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.db import get_db
from app.domain.upload_session.schema import (
    UploadInitiateIn,
    UploadInitiateOut,
    PresignPartIn,
    PresignPartOut,
    UploadPartOut,
    UploadPartsOut,
    CompleteUploadIn,
    CompletePartIn,
    UploadStatusOut,
    CompleteUploadOut,
)

from app.services.storage_service import StorageService
from app.services.upload_service import UploadService
from app.dependencies.tenant_dependency import get_current_tenant
from app.domain.tenant.model import Tenant


def get_upload_service(db: Session = Depends(get_db)) -> UploadService:
    return UploadService(db=db)


router = APIRouter()


@router.post("/multipart/initiate", response_model=UploadInitiateOut)
def initiate_upload(
    payload: UploadInitiateIn,
    service: UploadService = Depends(get_upload_service),
    current_tenant: Tenant = Depends(get_current_tenant),
):
    try:
        session = service.initiate(
            tenant_id=current_tenant.id,
            filename=payload.filename,
            content_type=payload.content_type,
            size_bytes=payload.size_bytes,
        )
        return UploadInitiateOut(
            upload_id=session.id,
            bucket=session.bucket,
            key=session.object_key,
            part_size_bytes=int(session.part_size_bytes),
            expires_at=session.expires_at,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{upload_id}/parts/presign", response_model=PresignPartOut)
def presign_part(
    upload_id: UUID,
    payload: PresignPartIn,
    service: UploadService = Depends(get_upload_service),
):
    try:
        url = service.presign_part(
            upload_id=upload_id, part_number=int(payload.part_number)
        )
        return PresignPartOut(signed_url=url, expires_in=600)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{upload_id}/parts", response_model=UploadPartsOut)
def list_uploaded_parts(
    upload_id: UUID,
    service: UploadService = Depends(get_upload_service),
):
    try:
        parts = service.list_parts(upload_id=upload_id)
        return UploadPartsOut(parts=[UploadPartOut(**p) for p in parts])
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{upload_id}/complete", response_model=CompleteUploadOut)
def complete_upload(
    upload_id: UUID,
    payload: CompleteUploadIn,
    service: UploadService = Depends(get_upload_service),
):
    try:
        session = service.complete(
            upload_id=upload_id,
            parts=[
                {"part_number": p.part_number, "etag": p.etag} for p in payload.parts
            ],
        )

        head = service.storage_service.head_object(
            bucket=session.bucket, key=session.object_key
        )
        size = int(head["ContentLength"])

        return CompleteUploadOut(
            status=session.status,
            bucket=session.bucket,
            key=session.object_key,
            size_bytes=size,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{upload_id}", response_model=UploadStatusOut)
def get_upload_status(
    upload_id: UUID,
    service: UploadService = Depends(get_upload_service),
):
    try:
        s = service.get_status(upload_id=upload_id)
        return UploadStatusOut(
            upload_id=s.id,
            status=s.status,
            filename=s.filename,
            content_type=s.content_type,
            size_bytes_expected=int(s.size_bytes_expected),
            bucket=s.bucket,
            key=s.object_key,
            created_at=s.created_at,
            expires_at=s.expires_at,
            uploaded_at=s.uploaded_at,
            completed_at=s.completed_at,
            processing_job_id=s.processing_job_id,
            error_code=s.error_code,
            error_message=s.error_message,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{upload_id}/abort")
def abort_upload(
    upload_id: UUID,
    service: UploadService = Depends(get_upload_service),
):
    try:
        s = service.abort(upload_id=upload_id)
        return {"upload_id": str(s.id), "status": s.status}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

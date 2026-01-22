import uuid
from fastapi import APIRouter, Depends, Query
from app.dependencies.jobs_dependency import get_job_service
from app.services.jobs_service import JobService
from app.domain.jobs.schema import JobResponse, JobListResponse
from app.domain.tenant.model import Tenant
from app.dependencies.tenant_dependency import get_current_tenant

router = APIRouter()


@router.get("/", response_model=JobListResponse)
def get_all_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=200),
    status: str | None = Query(None),
    jobs_service: JobService = Depends(get_job_service),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> JobListResponse:
    return jobs_service.list_jobs(
        tenant_id=current_tenant.id, skip=skip, limit=limit, status=status
    )


@router.get("/{job_id}", response_model=JobResponse)
def get_job_metadata(
    job_id: uuid.UUID,
    current_tenant: Tenant = Depends(get_current_tenant),
    jobs_service: JobService = Depends(get_job_service),
):
    return jobs_service.get_job(tenant_id=current_tenant.id, job_id=job_id)

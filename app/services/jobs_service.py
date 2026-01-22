import uuid
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repository.jobs_repository import JobRepository
from app.domain.jobs.schema import JobCreate, JobListResponse, JobResponse
from app.domain.jobs.model import JobObject


class JobService:

    def __init__(self, db: Session):
        self.repo = JobRepository(db=db)

    def create_job(self, payload: JobCreate) -> JobResponse:
        data = JobObject(
            tenant_id=payload.tenant_id,
            file_id=payload.file_id,
            job_type=payload.job_type,
            status=payload.status,
            error_message=payload.error_message,
        )
        result = self.repo.create_job(data=data)
        return JobResponse.model_validate(result)

    def get_job(self, tenant_id: uuid.UUID, job_id: uuid.UUID) -> JobResponse:
        obj = self.repo.get_job_by_id(tenant_id=tenant_id, job_id=job_id)
        if not obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Job not found"
            )

        return JobResponse.model_validate(obj)

    def list_jobs(
        self,
        tenant_id: uuid.UUID,
        skip: int,
        limit: int,
        status: str | None = None,
    ) -> JobListResponse:
        items = self.repo.list_jobs(
            tenant_id=tenant_id, skip=skip, limit=limit, status=status
        )
        total = self.repo.count_jobs(tenant_id=tenant_id, status=status)

        return JobListResponse(
            items=[JobResponse.model_validate(x) for x in items],
            total=total,
        )

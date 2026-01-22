from typing import List, Optional
import uuid
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.domain.jobs.model import JobObject


class JobRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_job(self, data: JobObject) -> JobObject:
        self.db.add(data)
        self.db.commit()
        self.db.refresh(data)
        return data

    def get_job_by_id(
        self, tenant_id: uuid.UUID, job_id: uuid.UUID
    ) -> Optional[JobObject]:
        return (
            self.db.query(JobObject)
            .filter(JobObject.id == job_id, JobObject.tenant_id == tenant_id)
            .first()
        )

    def list_jobs(
        self,
        tenant_id: uuid.UUID,
        skip: int,
        limit: int,
        status: str | None = None,
    ) -> List[JobObject]:
        q = self.db.query(JobObject).filter(JobObject.tenant_id == tenant_id)

        if status:
            q = q.filter(JobObject.status == status)

        return q.order_by(JobObject.created_at.desc()).offset(skip).limit(limit).all()

    def count_jobs(self, tenant_id: uuid.UUID, status: str | None = None) -> int:
        q = self.db.query(JobObject).filter(JobObject.tenant_id == tenant_id)

        if status:
            q = q.filter(JobObject.status == status)

        return q.count()

    def claim_next_pending_job(self) -> JobObject | None:
        row = self.db.execute(
            text(
                """
                UPDATE jobs.job_object
                SET status = 'RUNNING', updated_at = now()
                WHERE id = (
                    SELECT id
                    FROM jobs.job_object
                    WHERE status = 'PENDING'
                    ORDER BY created_at ASC
                    FOR UPDATE SKIP LOCKED
                    LIMIT 1
                )
                RETURNING id
            """
            )
        ).first()


        if not row:
            return None

        job_id = row[0]
        job = self.db.query(JobObject).filter(JobObject.id == job_id).first()

        return job

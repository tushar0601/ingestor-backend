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
                SET status = 'RUNNING',
                    locked_at = now(),
                    updated_at = now()
                WHERE id = (
                    SELECT id
                    FROM jobs.job_object
                    WHERE status = 'PENDING'
                    AND next_run_at <= now()
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
        return self.db.query(JobObject).filter(JobObject.id == job_id).first()

    def mark_failed_with_retry(self, job_id, error: str) -> None:
        sql = text(
            """
            UPDATE jobs.job_object
            SET
                attempts = attempts + 1,
                last_error = :err,
                status = CASE
                    WHEN (attempts + 1) < max_attempts THEN 'PENDING'
                    ELSE 'FAILED'
                END,
                next_run_at = CASE
                    WHEN (attempts + 1) < max_attempts THEN now() + (make_interval(secs => LEAST(power(2, attempts + 1)::int, 300)))
                    ELSE next_run_at
                END,
                locked_at = NULL,
                updated_at = now()
            WHERE id = :job_id
        """
        )
        self.db.execute(sql, {"job_id": str(job_id), "err": error[:8000]})
        self.db.commit()

    def reap_stuck_jobs(self, timeout_seconds: int) -> int:
        sql = text(
            """
            UPDATE jobs.job_object
            SET
                status = 'PENDING',
                next_run_at = now(),
                attempts = attempts + 1,
                last_error = CASE
                    WHEN last_error IS NULL THEN 'Reaped due to timeout'
                    ELSE left(last_error || E'\n' || 'Reaped due to timeout', 8000)
                END,
                locked_at = NULL,
                updated_at = now()
            WHERE status = 'RUNNING'
              AND locked_at IS NOT NULL
              AND locked_at < (now() - make_interval(secs => :timeout_seconds))
        """
        )
        res = self.db.execute(sql, {"timeout_seconds": timeout_seconds})
        self.db.commit()
        return res.rowcount or 0

    def mark_succeeded(self, job_id) -> None:
        self.db.execute(
            text(
                """
                UPDATE jobs.job_object
                SET status = 'SUCCEEDED',
                    last_error = NULL,
                    locked_at = NULL,
                    updated_at = now()
                WHERE id = :job_id
            """
            ),
            {"job_id": str(job_id)},
        )
        self.db.commit()

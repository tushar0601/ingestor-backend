import time
from sqlalchemy.orm import Session

from app.domain import models
from app.domain.jobs.model import JobObject
from app.domain.files.model import FileObject
from app.core.db import SessionLocal
from app.repository.jobs_repository import JobRepository
from app.repository.file_repository import FileRepository

POLL_INTERVAL_SECONDS = 1


def run_file_processor_worker() -> None:
    while True:
        db: Session = SessionLocal()
        job: JobObject | None = None

        try:
            job_repo = JobRepository(db=db)
            file_repo = FileRepository(db=db)

            job = job_repo.claim_next_pending_job()
            if job is None:
                time.sleep(POLL_INTERVAL_SECONDS)
                continue

            file_obj: FileObject | None = file_repo.get_file_by_id(
                tenant_id=job.tenant_id,
                file_id=job.file_id,
            )

            if file_obj is None:
                job.status = "FAILED"
                job.error_message = "File not found for job"
                db.commit()
                continue

            file_obj.status = "PROCESSING"
            db.commit()

            time.sleep(2)

            file_obj.status = "PROCESSED"
            file_obj.file_metadata = {"processed": True}
            db.commit()

            job.status = "SUCCEEDED"
            job.error_message = None
            db.commit()

        except Exception as e:
            db.rollback()
            if job is not None:
                try:
                    job.status = "FAILED"
                    job.error_message = str(e)[:2000]
                    db.commit()
                except Exception:
                    db.rollback()
        finally:
            db.close()


if __name__ == "__main__":
    run_file_processor_worker()

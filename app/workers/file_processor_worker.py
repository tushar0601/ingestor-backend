import time
from sqlalchemy.orm import Session

from app.domain.jobs.model import JobObject
from app.domain.files.model import FileObject
from app.domain import models
from app.core.db import SessionLocal
from app.core.config import settings
from app.repository.jobs_repository import JobRepository
from app.repository.file_repository import FileRepository
from app.processors.dispatch import process_file
from app.services.storage_service import StorageService
from app.processors.errors import NonRetryableProcessingError

POLL_INTERVAL_SECONDS = 1

from sqlalchemy.exc import SQLAlchemyError
import traceback


def run_file_processor_worker() -> None:
    loop_count = 0
    storage_service = StorageService()

    while True:
        db: Session = SessionLocal()
        job: JobObject | None = None

        try:
            job_repo = JobRepository(db=db)
            file_repo = FileRepository(db=db)

            loop_count += 1
            if loop_count % settings.REAP_EVERY_N_LOOPS == 0:
                job_repo.reap_stuck_jobs(
                    timeout_seconds=settings.JOB_RUN_TIMEOUT_SECONDS
                )

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
                job.last_error = "File not found for job"
                job.locked_at = None
                db.commit()
                continue

            if file_obj.status == "PROCESSED":
                job_repo.mark_succeeded(job_id=job.id)
                continue

            if file_obj.status != "UPLOADED":
                job_repo.mark_failed_with_retry(
                    job_id=job.id,
                    error=f"Cannot process file in status={file_obj.status}",
                )
                continue

            file_obj.status = "PROCESSING"
            try:
                db.commit()
            except SQLAlchemyError as e:
                traceback.print_exc()
                db.rollback()
                raise

            try:
                metadata, _ = process_file(file_obj, storage_service)
                file_obj.status = "PROCESSED"
                file_obj.file_metadata = metadata

                job.status = "SUCCEEDED"
                job.locked_at = None
                job.last_error = None

                db.commit()

            except NonRetryableProcessingError as e:
                db.rollback()

                file_obj.status = "FAILED"
                file_obj.file_metadata = {
                    "processor_error": str(e),
                }

                job.status = "FAILED"
                job.locked_at = None
                job.last_error = str(e)

                db.commit()

            except Exception as e:
                db.rollback()
                job_repo.mark_failed_with_retry(job_id=job.id, error=str(e))

        except Exception as e:
            db.rollback()
            if job is not None:
                try:
                    job_repo = JobRepository(db=db)
                    job_repo.mark_failed_with_retry(job_id=job.id, error=str(e))
                except Exception:
                    db.rollback()

        finally:
            db.close()


if __name__ == "__main__":
    run_file_processor_worker()

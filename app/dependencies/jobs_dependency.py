from fastapi import Depends
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.services.jobs_service import JobService


def get_job_service(db: Session = Depends(get_db)) -> JobService:
    return JobService(db=db)

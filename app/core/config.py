from __future__ import annotations

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):

    APP_NAME: str
    ENVIRONMENT: str
    DATABASE_URL: str
    S3_ENDPOINT_URL: str
    S3_ACCESS_KEY: str
    S3_SECRET_KEY: str
    S3_BUCKET: str
    S3_REGION: str
    API_KEY_HMAC_SECRET: str
    JOB_RUN_TIMEOUT_SECONDS: int
    REAP_EVERY_N_LOOPS: int
    MAX_UPLOAD_BYTES:int
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

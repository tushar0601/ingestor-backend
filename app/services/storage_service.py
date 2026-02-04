import mimetypes
from dataclasses import dataclass

import boto3
from botocore.client import Config
from botocore.exceptions import ClientError

from app.core.config import settings


@dataclass(frozen=True)
class UploadResult:
    bucket: str
    key: str
    etag: str | None
    size_bytes: int


class StorageService:

    def __init__(self) -> None:
        self._client = boto3.client(
            "s3",
            endpoint_url=settings.S3_ENDPOINT_URL,
            aws_access_key_id=settings.S3_ACCESS_KEY,
            aws_secret_access_key=settings.S3_SECRET_KEY,
            region_name=settings.S3_REGION,
            config=Config(signature_version="s3v4"),
        )

    def upload_fileobj(
        self, *, fileobj, key: str, content_type: str | None = None
    ) -> UploadResult:
        ct = content_type or mimetypes.guess_type(key)[0] or "application/octet-stream"

        self._client.upload_fileobj(
            Fileobj=fileobj,
            Bucket=settings.S3_BUCKET,
            Key=key,
            ExtraArgs={"ContentType": ct},
        )

        head = self._client.head_object(
            Bucket=settings.S3_BUCKET,
            Key=key,
        )

        return UploadResult(
            bucket=settings.S3_BUCKET,
            key=key,
            etag=head.get("ETag"),
            size_bytes=int(head["ContentLength"]),
        )

    def get_object(self, key: str):
        return self._client.get_object(Bucket=settings.S3_BUCKET, Key=key)

    def download_bytes(
        self, storage_path: str, *, max_bytes: int | None = None
    ) -> bytes:
        """
        Download object content into memory.
        For Phase 2 only (small files). Use max_bytes to prevent OOM.
        """
        try:
            if max_bytes is not None:
                head = self._client.head_object(
                    Bucket=settings.S3_BUCKET, Key=storage_path
                )
                size = int(head["ContentLength"])
                if size > max_bytes:
                    raise ValueError(
                        f"Object too large: {size} bytes > max_bytes={max_bytes}"
                    )

            obj = self._client.get_object(Bucket=settings.S3_BUCKET, Key=storage_path)
            body = obj["Body"].read()

            if max_bytes is not None and len(body) > max_bytes:
                raise ValueError(
                    f"Downloaded too many bytes: {len(body)} > max_bytes={max_bytes}"
                )

            return body
        except ClientError as e:
            raise

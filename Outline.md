
You can tweak wording to sound more “you”, but structurally this is good.

---

## 0.3 `docs/design-overview.md` – initial design doc

Create `docs/design-overview.md`:

```markdown
# Ingestor – Design Overview

## 1. Problem Statement

Client applications often need to:
- Upload large files (images, PDFs, CSVs, etc.) reliably.
- Offload processing work (thumbnails, text extraction, CSV stats, etc.).
- Avoid building and maintaining their own file pipelines and workers.
- Keep multi-tenant isolation and basic compliance (per-tenant separation, quotas).

Ingestor provides a backend platform that abstracts:
- Reliable file ingestion (small + large).
- Asynchronous processing pipelines.
- File metadata and access via API.

---

## 2. Goals

- Support both **small** and **large** file uploads.
- Decouple upload from processing via a **job queue** and **workers**.
- Store all **file metadata and processing status** in PostgreSQL.
- Integrate with **S3-compatible object storage** (MinIO initially).
- Provide **multi-tenant isolation** with per-tenant API keys and limits.
- Provide **webhooks** for file processing completion.

### Non-Goals (for now)

- Full-blown UI / dashboard (only minimal if time permits).
- Extreme optimizations for billions of files.
- Complex ACLs / fine-grained RBAC.
- Perfect resumable multipart upload implementation (initially modeled, optionally partially implemented).

---

## 3. High-level Architecture

Components:

- **API Service (FastAPI)**  
  - Handles authentication (API keys).  
  - Exposes REST APIs for:
    - Small-file upload.
    - Large-file upload initiation and completion.
    - Listing files and jobs.
    - Registering webhooks.  

- **Storage Service (MinIO / S3-compatible)**  
  - Stores raw and processed file objects.
  - Generates signed URLs for uploads and downloads.

- **Database (PostgreSQL)**  
  - `tenants`: tenant records and limits.
  - `files`: file metadata and status.
  - `jobs`: async job tracking.
  - `webhooks`: registered callback URLs.
  - (Optional): `upload_sessions` for multipart uploads.

- **Queue + Workers (Redis + RQ)**  
  - Queue for processing jobs.
  - Worker processes:
    - Download file from storage.
    - Run appropriate processor (image/PDF/CSV).
    - Upload processed artifacts.
    - Update metadata and job status.
    - Trigger webhook events.

- **(Optional) Webhook Delivery Worker**  
  - Handles retry logic and backoff for webhooks.

---

## 4. Data Model (Initial)

### 4.1 Tenants

- `id` (UUID)
- `name`
- `api_key_hash`
- `max_file_size_mb`
- `created_at`, `updated_at`

### 4.2 Files

- `id` (UUID)
- `tenant_id` (FK → tenants.id)
- `original_filename`
- `content_type`
- `size_bytes`
- `storage_path` (e.g. `tenant-{id}/raw/{file_id}`)
- `status` (`PENDING_UPLOAD`, `UPLOADED`, `PROCESSING`, `PROCESSED`, `FAILED`)
- `upload_mode` (`DIRECT`, `FORM`)
- `metadata` (JSONB – type-specific info)
- `created_at`, `updated_at`

### 4.3 Jobs

- `id` (UUID)
- `tenant_id` (FK)
- `file_id` (FK)
- `job_type` (`PROCESS_FILE`)
- `status` (`PENDING`, `RUNNING`, `COMPLETED`, `FAILED`)
- `error_message` (nullable)
- `created_at`, `updated_at`

### 4.4 Webhooks (later phase)

- `id` (UUID)
- `tenant_id` (FK)
- `url`
- `secret`
- `event_types` (JSON array of strings, e.g. `["file.processed"]`)
- `created_at`, `updated_at`

---

## 5. Key Flows

### 5.1 Small File Upload Flow (≤ 20MB)

1. Client calls `POST /api/v1/files/upload` with `multipart/form-data`:
   - Includes file and optional metadata.
2. API authenticates tenant via API key.
3. API streams file to storage via `StorageService`.
4. API inserts `files` row with `status = "UPLOADED"`.
5. API creates `jobs` row and enqueues a `PROCESS_FILE` job.
6. Worker processes file and updates job + file status.

### 5.2 Large File Upload Flow (Signed URL, single PUT)

1. Client calls `POST /api/v1/files/initiate` with filename, content_type, size.
2. API:
   - Validates limits.
   - Creates `files` row with `status = "PENDING_UPLOAD"`.
   - Computes storage key.
   - Generates signed `PUT` URL via `StorageService`.
3. Client uploads file directly to storage using signed URL.
4. Client calls `POST /api/v1/files/{file_id}/complete`.
5. API:
   - (Optionally) verifies object existence.
   - Sets `status = "UPLOADED"`.
   - Creates `jobs` row and enqueues `PROCESS_FILE`.

### 5.3 Processing Flow

1. Worker picks up `PROCESS_FILE(file_id)` job.
2. Worker:
   - Loads file metadata.
   - Downloads/streams file from storage.
   - Selects processor:
     - `ImageProcessor`
     - `PdfProcessor`
     - `CsvProcessor`
   - Runs processing pipeline:
     - Extract metadata.
     - Generate derived artifacts (thumbnails, previews, summaries).
     - Upload artifacts back to storage.
     - Update `files.metadata` and `files.status`.
3. Worker marks job as `COMPLETED` or `FAILED`.
4. If enabled, enqueue webhook delivery.

### 5.4 Webhook Flow (Later Phase)

1. Tenant registers webhook via `POST /api/v1/webhooks`.
2. When a `file.processed` event occurs:
   - Worker enqueues webhook delivery job.
3. Webhook worker:
   - Builds payload (file_id, status, metadata).
   - Signs payload with tenant secret.
   - Sends HTTP POST to tenant URL.
   - Retries on failure with backoff.

---

## 6. Non-Functional Requirements

- **Scalability**
  - API and worker services can run multiple replicas.
  - Storage is S3-compatible; can move from MinIO to cloud provider.
- **Reliability**
  - Jobs are idempotent where possible.
  - Failures are logged and surfaced via job status.
- **Security**
  - Per-tenant API keys.
  - Signed URLs with expiry for upload/download.
  - Tenant isolation at DB and storage key level.
- **Observability**
  - Structured logging including `tenant_id`, `file_id`, `job_id`.
  - Health endpoints for API and worker.
  - Basic metrics (to be refined later).

---

## 7. Open Questions / Future Work

- Full multipart/resumable upload support for extremely large files.
- Role-based access control within a tenant (e.g., admin vs viewer).
- Advanced processing pipelines (OCR, NLP, etc.).
- Production deployment strategy (Kubernetes, autoscaling workers).

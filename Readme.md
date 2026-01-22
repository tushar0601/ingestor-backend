# Ingestor – File Upload & Processing Platform

Ingestor is a backend-focused, multi-tenant file ingestion and processing platform.

Client applications can:
- Upload small files directly via API.
- Upload large files via signed URLs, directly to object storage.
- Trigger asynchronous processing pipelines for images, PDFs, and CSVs.
- Query file metadata and processing status.
- Receive webhooks when processing completes.

---

## High-level Features (Planned)

- Multi-tenant architecture with API-key based authentication.
- File upload flows:
  - Direct small-file upload via FastAPI (`multipart/form-data`).
  - Large-file upload via signed URLs (control plane vs data plane).
- Asynchronous processing with workers and a job queue:
  - Image processing: metadata + thumbnails.
  - PDF processing: page count, metadata, optional preview.
  - CSV processing: row count, columns, basic statistics.
- Object storage integration (MinIO, S3-compatible).
- Webhooks for file-processed notifications.
- Basic observability: structured logs, simple metrics, health checks.

---

## Tech Stack

- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL + SQLAlchemy + Alembic
- **Queue / Workers**: Redis + RQ (or Celery)
- **Object Storage**: MinIO (S3-compatible)
- **Auth**: API keys (per-tenant)
- **Infra**: Docker + docker-compose
- **(Optional later)**: Next.js mini dashboard for browsing files and metadata

---

## Architecture Overview

At a high level:

- The **API service** handles authentication, file initiation, metadata, and job creation.
- The **storage layer** (MinIO) stores raw and processed file objects.
- The **job queue + workers** perform asynchronous processing.
- The **database** stores tenants, files, jobs, webhooks, and metadata.
- The **webhook service** (can be part of worker) notifies client systems when processing completes.

**Core flows:**
1. Small-file upload → API → Storage → Enqueue processing job.
2. Large-file upload → API issues signed URL → Client uploads to storage → API marks complete + enqueues job.
3. Worker consumes job → runs processor (image/PDF/CSV) → updates metadata → triggers webhooks.

---

## Project Roadmap (Option B – 3–4 weeks)

**Week 1 – Foundations**
- Set up repo, Docker, FastAPI skeleton.
- PostgreSQL + Alembic migrations.
- MinIO integration + small-file upload endpoint (`/files/upload`).
- Basic `files` table + metadata.

**Week 2 – Async & Processing**
- Jobs table + Redis + worker service.
- Asynchronous job processing pipeline.
- Implement basic image, PDF, and CSV processors.
- Job status endpoint.

**Week 3 – Large Uploads & Tenancy**
- Signed URL upload flow (`/files/initiate` → direct PUT → `/files/{id}/complete`).
- Multi-tenant model (`tenants`, API keys, per-tenant isolation).
- Enforce per-tenant file size and type limits.

**Week 4 – Platform Polish (Optional but Recommended)**
- Webhooks for processing completion.
- Structured logging + basic metrics.
- Clean-up & documentation.
- (Optional) Basic Next.js dashboard to list and inspect files.

---

## Local Development (placeholder)

> This section will be refined later as services are added.

Basic plan:

```bash
# Start services
docker-compose up -d

# Apply migrations
alembic upgrade head

# Run API locally
uvicorn app.main:app --reload



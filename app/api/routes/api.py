from fastapi import APIRouter
from app.api.routes.tenant import router as tenant_router
from app.api.routes.files import router as file_router
from app.api.routes.jobs import router as jobs_router

router = APIRouter()
router.include_router(tenant_router, prefix="/tenant", tags=["Tenant"])
router.include_router(file_router, prefix="/file", tags=["File"])
router.include_router(jobs_router, prefix="/jobs", tags=["Jobs"])

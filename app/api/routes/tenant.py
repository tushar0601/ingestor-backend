from fastapi import APIRouter, Depends
from app.services.tenant_service import TenantService
from app.dependencies.tenant_dependency import get_tenant_service
from app.domain.tenant.schema import TenantListResponse, TenantCreate, TenantResponse

router = APIRouter()

@router.get("/", response_model=TenantListResponse)
def get_all_tenants(service: TenantService = Depends(get_tenant_service)) -> TenantListResponse:
    return service.get_all_tenants()

@router.post("/", response_model=TenantResponse, status_code=201)
def create_tenant(
    payload: TenantCreate,
    service: TenantService = Depends(get_tenant_service),
) -> TenantResponse:
    return service.create_tenant(payload=payload)
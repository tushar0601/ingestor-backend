
from sqlalchemy.orm import Session

from app.repository.tenant_repository import TenantRepository
from app.core.security import hash_api_key
from app.domain.tenant.schema import TenantListResponse, TenantResponse, TenantCreate
from app.domain.tenant.model import Tenant

class TenantService:

    def __init__(self,db: Session):
        self.repo = TenantRepository(db=db)

    def get_all_tenants(self):
        tenants = self.repo.get_all_tenants()
        items = [TenantResponse.model_validate(t) for t in tenants]
        return TenantListResponse(items=items,total=len(items))
    
    def create_tenant(self, payload: TenantCreate) -> TenantResponse:
        hashed = hash_api_key(api_key=payload.api_key)

        tenant = Tenant(
            name=payload.name,
            api_key_hash=hashed,
            max_file_size_mb=payload.max_file_size_mb,
        )

        created = self.repo.create_tenant(data=tenant)
        return TenantResponse.model_validate(created)

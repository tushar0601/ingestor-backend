import uuid
import hmac
from app.services.tenant_service import TenantService
from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.core.security import hash_api_key
from app.repository.tenant_repository import TenantRepository
from app.domain.tenant.model import Tenant

def get_tenant_service(db: Session = Depends(get_db)) -> TenantService:
    return TenantService(db=db)

def get_current_tenant(
        x_tenant_id: str | None = Header(default=None, alias="X-Tenant-Id"),
        x_api_key: str | None = Header(default=None, alias="X-API-Key"),
        db: Session = Depends(get_db)
) -> Tenant:
    
    if not x_tenant_id or not x_tenant_id.strip():
        raise HTTPException(status_code=401,detail="Missing X-Tenant-Id")
    
    if not x_api_key or not x_api_key.strip():
        raise HTTPException(status_code=401,detail="Missing X-API-Key")
    
    try:
        tenant_id = uuid.UUID(x_tenant_id.strip())
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid X-Tenant-Id")

    repo = TenantRepository(db=db)
    tenant = repo.get_by_tenant_id(tenant_id=tenant_id)

    if not tenant:
        raise HTTPException(status_code=401,detail="Invalid Credentials")
    
    presented_hash = hash_api_key(x_api_key.strip())

    if not hmac.compare_digest(presented_hash, tenant.api_key_hash):
        raise HTTPException(status_code=401, detail="Invalid Credentials")
    
    return tenant
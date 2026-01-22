import uuid
from sqlalchemy.orm import Session
from typing import List, Optional
from app.domain.tenant.model import Tenant


class TenantRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all_tenants(self) -> List[Tenant]:
        return self.db.query(Tenant).all()

    def get_by_tenant_id(self, tenant_id: uuid.UUID) -> Optional[Tenant]:
        return self.db.query(Tenant).filter(Tenant.id == tenant_id).one_or_none()

    def create_tenant(self, data: Tenant) -> Tenant:
        self.db.add(data)
        self.db.flush()
        self.db.commit()
        self.db.refresh(data)
        return data

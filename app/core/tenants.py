from sqlalchemy.orm import Session
from app.models import Tenant

def load_tenant(db: Session, tenant_id: str) -> Tenant | None:
    return db.query(Tenant).filter(Tenant.id == tenant_id).one_or_none()
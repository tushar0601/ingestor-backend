from sqlalchemy.orm import Session
from uuid import UUID
from app.domain.upload_session.model import UploadSession

class UploadSessionRepository:

    def __init__(self, db: Session):
        self.db = db
    
    def create(self, session: UploadSession) -> UploadSession:
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session
    
    def get_by_id(self, upload_id: UUID) -> UploadSession | None:
        return self.db.query(UploadSession).filter(UploadSession.id == upload_id).one_or_none()
    
    def update(self,session: UploadSession) -> UploadSession:
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session
    
    
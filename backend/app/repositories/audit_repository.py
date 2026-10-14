from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from app.models.audit import AuditLog
from app.repositories.base_repository import BaseRepository


class AuditRepository(BaseRepository[AuditLog]):
    def __init__(self, db: Session):
        super().__init__(AuditLog, db)

    def log_action(
        self,
        action: str,
        entity_type: str,
        user_id: Optional[int] = None,
        entity_id: Optional[int] = None,
        metadata_json: Optional[str] = None,
    ) -> AuditLog:
        audit_entry = AuditLog(
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            metadata_json=metadata_json,
        )
        return self.create(audit_entry)

    def get_recent_logs(self, limit: int = 50, entity_type: Optional[str] = None) -> List[AuditLog]:
        query = self.db.query(AuditLog).options(joinedload(AuditLog.user))
        if entity_type:
            query = query.filter(AuditLog.entity_type == entity_type)
        return query.order_by(AuditLog.timestamp.desc()).limit(limit).all()

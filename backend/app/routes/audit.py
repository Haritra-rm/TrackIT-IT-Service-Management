from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.dashboard import AuditLogResponse
from app.schemas.common import ApiResponse
from app.repositories.audit_repository import AuditRepository
from app.core.dependencies import require_admin
from app.models.user import User

router = APIRouter(prefix="/audit-logs", tags=["Audit Logs"])


@router.get(
    "",
    response_model=ApiResponse[List[AuditLogResponse]],
    summary="Get recent system audit logs (Admin only)",
)
def get_audit_logs(
    limit: int = Query(50, ge=1, le=200),
    entity_type: Optional[str] = Query(None),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    repo = AuditRepository(db)
    logs = repo.get_recent_logs(limit=limit, entity_type=entity_type)
    data = [
        AuditLogResponse(
            id=log.id,
            user_id=log.user_id,
            user_name=log.user.name if log.user else "System",
            action=log.action,
            entity_type=log.entity_type,
            entity_id=log.entity_id,
            timestamp=log.timestamp,
            metadata_json=log.metadata_json,
        )
        for log in logs
    ]
    return ApiResponse(success=True, data=data)

from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.user import User
from app.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository handling all User database queries and state changes."""

    def __init__(self, db: Session):
        super().__init__(User, db)

    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email.lower().strip()).first()

    def get_by_id(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_users_by_role(self, role: str) -> List[User]:
        return self.db.query(User).filter(User.role == role).all()

    def get_active_agents(self) -> List[User]:
        return (
            self.db.query(User)
            .filter(User.role.in_(["SUPPORT_AGENT", "ADMIN"]), User.is_active == True)
            .order_by(User.name.asc())
            .all()
        )

    def search_users(self, search: Optional[str] = None, role: Optional[str] = None, is_active: Optional[bool] = None, skip: int = 0, limit: int = 50) -> List[User]:
        query = self.db.query(User)
        if search:
            term = f"%{search.strip()}%"
            query = query.filter((User.name.ilike(term)) | (User.email.ilike(term)))
        if role:
            query = query.filter(User.role == role)
        if is_active is not None:
            query = query.filter(User.is_active == is_active)
        return query.order_by(User.id.desc()).offset(skip).limit(limit).all()

    def count_users(self, search: Optional[str] = None, role: Optional[str] = None, is_active: Optional[bool] = None) -> int:
        query = self.db.query(User)
        if search:
            term = f"%{search.strip()}%"
            query = query.filter((User.name.ilike(term)) | (User.email.ilike(term)))
        if role:
            query = query.filter(User.role == role)
        if is_active is not None:
            query = query.filter(User.is_active == is_active)
        return query.count()

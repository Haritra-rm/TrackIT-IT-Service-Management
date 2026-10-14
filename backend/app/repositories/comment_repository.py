from typing import List
from sqlalchemy.orm import Session, joinedload
from app.models.comment import Comment
from app.repositories.base_repository import BaseRepository


class CommentRepository(BaseRepository[Comment]):
    def __init__(self, db: Session):
        super().__init__(Comment, db)

    def get_by_ticket_id(self, ticket_id: int) -> List[Comment]:
        return (
            self.db.query(Comment)
            .options(joinedload(Comment.user))
            .filter(Comment.ticket_id == ticket_id)
            .order_by(Comment.created_at.asc())
            .all()
        )

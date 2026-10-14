from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.category import Category
from app.repositories.base_repository import BaseRepository


class CategoryRepository(BaseRepository[Category]):
    def __init__(self, db: Session):
        super().__init__(Category, db)

    def get_by_name(self, name: str) -> Optional[Category]:
        return self.db.query(Category).filter(Category.name.ilike(name.strip())).first()

    def get_active_categories(self) -> List[Category]:
        return self.db.query(Category).filter(Category.is_active == True).order_by(Category.name.asc()).all()

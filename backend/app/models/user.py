from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database.base import Base


class UserRole:
    EMPLOYEE = "EMPLOYEE"
    SUPPORT_AGENT = "SUPPORT_AGENT"
    ADMIN = "ADMIN"

    ALL_ROLES = [EMPLOYEE, SUPPORT_AGENT, ADMIN]


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), default=UserRole.EMPLOYEE, nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    created_tickets = relationship("Ticket", back_populates="creator", foreign_keys="[Ticket.created_by]")
    assigned_tickets = relationship("Ticket", back_populates="assignee", foreign_keys="[Ticket.assigned_to]")
    comments = relationship("Comment", back_populates="user")
    status_changes = relationship("TicketStatusHistory", back_populates="author")
    audit_logs = relationship("AuditLog", back_populates="user")

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}')>"

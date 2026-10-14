from datetime import datetime
from typing import Optional, List, Tuple, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, or_, desc, asc

from app.models.ticket import Ticket, TicketStatus, TicketPriority
from app.models.status_history import TicketStatusHistory
from app.models.category import Category
from app.models.user import User
from app.repositories.base_repository import BaseRepository


class TicketRepository(BaseRepository[Ticket]):
    def __init__(self, db: Session):
        super().__init__(Ticket, db)

    def get_by_id_with_relations(self, ticket_id: int) -> Optional[Ticket]:
        """Fetch a ticket with eager-loaded relationships to avoid N+1 queries."""
        return (
            self.db.query(Ticket)
            .options(
                joinedload(Ticket.category),
                joinedload(Ticket.creator),
                joinedload(Ticket.assignee),
                joinedload(Ticket.comments),
                joinedload(Ticket.status_history),
            )
            .filter(Ticket.id == ticket_id)
            .first()
        )

    def search_and_filter(
        self,
        search: Optional[str] = None,
        ticket_id: Optional[int] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        category_id: Optional[int] = None,
        created_by: Optional[int] = None,
        assigned_to: Optional[int] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        skip: int = 0,
        limit: int = 20,
    ) -> Tuple[List[Ticket], int]:
        """
        Advanced query with indexing optimization, dynamic filters, pagination, and sorting.
        Returns (list_of_tickets, total_count).
        """
        query = self.db.query(Ticket).options(
            joinedload(Ticket.category),
            joinedload(Ticket.creator),
            joinedload(Ticket.assignee),
        )

        if ticket_id is not None:
            query = query.filter(Ticket.id == ticket_id)
        elif search:
            search_clean = search.strip()
            # If search is a numeric digit, allow direct match on ticket id or substring in title
            if search_clean.isdigit():
                query = query.filter(
                    or_(
                        Ticket.id == int(search_clean),
                        Ticket.title.ilike(f"%{search_clean}%"),
                        Ticket.description.ilike(f"%{search_clean}%"),
                    )
                )
            else:
                query = query.filter(
                    or_(
                        Ticket.title.ilike(f"%{search_clean}%"),
                        Ticket.description.ilike(f"%{search_clean}%"),
                    )
                )

        if status:
            query = query.filter(Ticket.status == status)

        if priority:
            query = query.filter(Ticket.priority == priority)

        if category_id:
            query = query.filter(Ticket.category_id == category_id)

        if created_by:
            query = query.filter(Ticket.created_by == created_by)

        if assigned_to:
            query = query.filter(Ticket.assigned_to == assigned_to)

        if from_date:
            query = query.filter(Ticket.created_at >= from_date)

        if to_date:
            query = query.filter(Ticket.created_at <= to_date)

        total = query.count()

        # Sorting logic
        sort_column = getattr(Ticket, sort_by, Ticket.created_at)
        if sort_order.lower() == "asc":
            query = query.order_by(asc(sort_column))
        else:
            query = query.order_by(desc(sort_column))

        items = query.offset(skip).limit(limit).all()
        return items, total

    def record_status_change(
        self,
        ticket_id: int,
        old_status: Optional[str],
        new_status: str,
        changed_by: int,
    ) -> TicketStatusHistory:
        history = TicketStatusHistory(
            ticket_id=ticket_id,
            old_status=old_status,
            new_status=new_status,
            changed_by=changed_by,
        )
        self.db.add(history)
        self.db.commit()
        self.db.refresh(history)
        return history

    def get_status_history(self, ticket_id: int) -> List[TicketStatusHistory]:
        return (
            self.db.query(TicketStatusHistory)
            .options(joinedload(TicketStatusHistory.author))
            .filter(TicketStatusHistory.ticket_id == ticket_id)
            .order_by(TicketStatusHistory.changed_at.asc())
            .all()
        )

    def get_status_counts(self, user_id: Optional[int] = None, role: Optional[str] = None) -> List[Dict[str, Any]]:
        query = self.db.query(Ticket.status, func.count(Ticket.id))
        if role == "EMPLOYEE" and user_id:
            query = query.filter(Ticket.created_by == user_id)
        elif role == "SUPPORT_AGENT" and user_id:
            query = query.filter(Ticket.assigned_to == user_id)

        results = query.group_by(Ticket.status).all()
        return [{"status": status, "count": count} for status, count in results]

    def get_priority_counts(self) -> List[Dict[str, Any]]:
        results = self.db.query(Ticket.priority, func.count(Ticket.id)).group_by(Ticket.priority).all()
        return [{"priority": priority, "count": count} for priority, count in results]

    def get_category_counts(self) -> List[Dict[str, Any]]:
        results = (
            self.db.query(Category.id, Category.name, func.count(Ticket.id))
            .join(Ticket, Ticket.category_id == Category.id, isouter=True)
            .group_by(Category.id, Category.name)
            .all()
        )
        return [
            {"category_id": cat_id, "category_name": cat_name, "count": count}
            for cat_id, cat_name, count in results
        ]

    def get_agent_performance_metrics(self) -> List[Dict[str, Any]]:
        """Compute performance metrics for each support agent."""
        agents = (
            self.db.query(User)
            .filter(User.role.in_(["SUPPORT_AGENT", "ADMIN"]))
            .all()
        )

        metrics = []
        now = datetime.now()

        for agent in agents:
            assigned_tickets = self.db.query(Ticket).filter(Ticket.assigned_to == agent.id).all()
            total_assigned = len(assigned_tickets)
            in_prog = sum(1 for t in assigned_tickets if t.status in [TicketStatus.IN_PROGRESS, TicketStatus.ASSIGNED])
            resolved = sum(1 for t in assigned_tickets if t.status in [TicketStatus.RESOLVED, TicketStatus.CLOSED])

            # Avg resolution time
            durations = []
            on_time_count = 0
            resolved_with_sla = 0

            for t in assigned_tickets:
                if t.resolved_at and t.created_at:
                    diff_hours = (t.resolved_at - t.created_at).total_seconds() / 3600.0
                    durations.append(diff_hours)
                    if t.due_at:
                        resolved_with_sla += 1
                        if t.resolved_at <= t.due_at:
                            on_time_count += 1

            avg_res_time = round(sum(durations) / len(durations), 2) if durations else 0.0
            sla_compliance = round((on_time_count / resolved_with_sla) * 100.0, 1) if resolved_with_sla > 0 else 100.0

            metrics.append({
                "agent_id": agent.id,
                "agent_name": agent.name,
                "agent_email": agent.email,
                "assigned_count": total_assigned,
                "in_progress_count": in_prog,
                "resolved_count": resolved,
                "avg_resolution_hours": avg_res_time,
                "sla_compliance_rate": sla_compliance,
            })

        return metrics

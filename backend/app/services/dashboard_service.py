from datetime import datetime, timezone
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.ticket import Ticket, TicketStatus, TicketPriority
from app.models.user import User, UserRole
from app.models.comment import Comment
from app.schemas.dashboard import (
    DashboardSummary,
    StatusCount,
    PriorityCount,
    CategoryCount,
    AgentPerformanceMetric,
)
from app.repositories.ticket_repository import TicketRepository
from app.repositories.category_repository import CategoryRepository
from app.services.sla_service import SLAService


class DashboardService:
    def __init__(self, db: Session):
        self.db = db
        self.ticket_repo = TicketRepository(db)
        self.category_repo = CategoryRepository(db)

    def get_summary(self, user: User) -> DashboardSummary:
        # Base query depends on role
        query = self.db.query(Ticket)
        if user.role == UserRole.EMPLOYEE:
            query = query.filter(Ticket.created_by == user.id)
        elif user.role == UserRole.SUPPORT_AGENT:
            # Agents see tickets assigned to them in their personal summary
            query = query.filter(Ticket.assigned_to == user.id)

        all_tickets = query.all()
        total = len(all_tickets)

        open_cnt = sum(1 for t in all_tickets if t.status == TicketStatus.OPEN)
        assigned_cnt = sum(1 for t in all_tickets if t.status == TicketStatus.ASSIGNED)
        in_prog_cnt = sum(1 for t in all_tickets if t.status == TicketStatus.IN_PROGRESS)
        resolved_cnt = sum(1 for t in all_tickets if t.status == TicketStatus.RESOLVED)
        closed_cnt = sum(1 for t in all_tickets if t.status == TicketStatus.CLOSED)
        reopened_cnt = sum(1 for t in all_tickets if t.status == TicketStatus.REOPENED)

        # SLA analysis
        breached_cnt = 0
        at_risk_cnt = 0
        on_track_cnt = 0
        resolution_durations = []

        now = datetime.now()

        for t in all_tickets:
            sla_info = SLAService.evaluate_sla_status(
                created_at=t.created_at,
                due_at=t.due_at,
                resolved_at=t.resolved_at,
                status=t.status,
            )
            if sla_info["is_breached"]:
                breached_cnt += 1
            elif sla_info["sla_status"] == "AT_RISK":
                at_risk_cnt += 1
            else:
                on_track_cnt += 1

            if t.resolved_at and t.created_at:
                diff_h = (t.resolved_at - t.created_at).total_seconds() / 3600.0
                resolution_durations.append(diff_h)

        sla_breach_rate = round((breached_cnt / total * 100.0), 1) if total > 0 else 0.0
        avg_res_time = round(sum(resolution_durations) / len(resolution_durations), 2) if resolution_durations else 0.0
        res_rate = round(((resolved_cnt + closed_cnt) / total * 100.0), 1) if total > 0 else 0.0

        # Average First Response Time: average time between ticket creation and first comment/assignment
        first_response_diffs = []
        for t in all_tickets:
            first_comment = (
                self.db.query(Comment)
                .filter(Comment.ticket_id == t.id, Comment.user_id != t.created_by)
                .order_by(Comment.created_at.asc())
                .first()
            )
            if first_comment and first_comment.created_at > t.created_at:
                first_response_diffs.append((first_comment.created_at - t.created_at).total_seconds() / 3600.0)

        avg_first_resp = round(sum(first_response_diffs) / len(first_response_diffs), 2) if first_response_diffs else round(avg_res_time * 0.25, 2)

        return DashboardSummary(
            total_tickets=total,
            open_tickets=open_cnt,
            assigned_tickets=assigned_cnt,
            in_progress_tickets=in_prog_cnt,
            resolved_tickets=resolved_cnt,
            closed_tickets=closed_cnt,
            reopened_tickets=reopened_cnt,
            sla_breached_count=breached_cnt,
            sla_at_risk_count=at_risk_cnt,
            sla_on_track_count=on_track_cnt,
            sla_breach_rate=sla_breach_rate,
            avg_resolution_time_hours=avg_res_time,
            avg_first_response_time_hours=avg_first_resp,
            resolution_rate=res_rate,
        )

    def get_tickets_by_status(self, user: User) -> List[StatusCount]:
        counts_data = self.ticket_repo.get_status_counts(user_id=user.id, role=user.role)
        total = sum(d["count"] for d in counts_data)

        # Standard list of statuses
        all_stat_map = {st: 0 for st in TicketStatus.ALL_STATUSES}
        for d in counts_data:
            all_stat_map[d["status"]] = d["count"]

        results = []
        for status, count in all_stat_map.items():
            pct = round((count / total * 100.0), 1) if total > 0 else 0.0
            results.append(StatusCount(status=status, count=count, percentage=pct))
        return results

    def get_tickets_by_priority(self) -> List[PriorityCount]:
        counts_data = self.ticket_repo.get_priority_counts()
        total = sum(d["count"] for d in counts_data)

        all_pri_map = {p: 0 for p in TicketPriority.ALL_PRIORITIES}
        for d in counts_data:
            all_pri_map[d["priority"]] = d["count"]

        results = []
        for priority, count in all_pri_map.items():
            pct = round((count / total * 100.0), 1) if total > 0 else 0.0
            results.append(PriorityCount(priority=priority, count=count, percentage=pct))
        return results

    def get_tickets_by_category(self) -> List[CategoryCount]:
        counts_data = self.ticket_repo.get_category_counts()
        total = sum(d["count"] for d in counts_data)

        results = []
        for d in counts_data:
            pct = round((d["count"] / total * 100.0), 1) if total > 0 else 0.0
            results.append(
                CategoryCount(
                    category_id=d["category_id"],
                    category_name=d["category_name"],
                    count=d["count"],
                    percentage=pct,
                )
            )
        return results

    def get_agent_performance(self) -> List[AgentPerformanceMetric]:
        metrics = self.ticket_repo.get_agent_performance_metrics()
        return [AgentPerformanceMetric(**m) for m in metrics]

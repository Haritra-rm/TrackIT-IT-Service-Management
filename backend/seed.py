import os
import sys
from datetime import datetime, timedelta, timezone

# Ensure backend package can be imported
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database.connection import engine
from app.database.session import SessionLocal
from app.database.base import Base
from app.core.security import get_password_hash
from app.models.user import User, UserRole
from app.models.category import Category
from app.models.ticket import Ticket, TicketStatus, TicketPriority
from app.models.comment import Comment
from app.models.status_history import TicketStatusHistory
from app.models.audit import AuditLog
from app.services.sla_service import SLAService
from app.core.logging import logger


def seed_database():
    """Seeds the database with realistic demo users, categories, tickets, comments, and history."""
    logger.info("Initializing database tables...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # Check if already seeded
        if db.query(User).count() > 0:
            logger.info("Database already seeded with data. Skipping.")
            return

        logger.info("Seeding Users...")
        # 1 Admin
        admin = User(
            name="Alexander Mitchell",
            email="admin@trackit.internal",
            password_hash=get_password_hash("Admin@123"),
            role=UserRole.ADMIN,
            is_active=True,
        )

        # 2 Support Agents
        agent1 = User(
            name="Sarah Jenkins",
            email="agent.sarah@trackit.internal",
            password_hash=get_password_hash("Agent@123"),
            role=UserRole.SUPPORT_AGENT,
            is_active=True,
        )
        agent2 = User(
            name="Johnathan Vance",
            email="agent.john@trackit.internal",
            password_hash=get_password_hash("Agent@123"),
            role=UserRole.SUPPORT_AGENT,
            is_active=True,
        )

        # 5 Employees
        emp1 = User(
            name="Alice Morgan",
            email="emp.alice@trackit.internal",
            password_hash=get_password_hash("Employee@123"),
            role=UserRole.EMPLOYEE,
            is_active=True,
        )
        emp2 = User(
            name="Bob Henderson",
            email="emp.bob@trackit.internal",
            password_hash=get_password_hash("Employee@123"),
            role=UserRole.EMPLOYEE,
            is_active=True,
        )
        emp3 = User(
            name="Carol Danvers",
            email="emp.carol@trackit.internal",
            password_hash=get_password_hash("Employee@123"),
            role=UserRole.EMPLOYEE,
            is_active=True,
        )
        emp4 = User(
            name="David Kim",
            email="emp.david@trackit.internal",
            password_hash=get_password_hash("Employee@123"),
            role=UserRole.EMPLOYEE,
            is_active=True,
        )
        emp5 = User(
            name="Emma Watson",
            email="emp.emma@trackit.internal",
            password_hash=get_password_hash("Employee@123"),
            role=UserRole.EMPLOYEE,
            is_active=True,
        )

        users = [admin, agent1, agent2, emp1, emp2, emp3, emp4, emp5]
        db.add_all(users)
        db.commit()
        for u in users:
            db.refresh(u)

        logger.info("Seeding Categories...")
        categories_data = [
            ("Hardware", "Physical computing equipment: laptops, monitors, docking stations, peripherals"),
            ("Software", "Licensed enterprise applications, developer tooling, OS installations"),
            ("Network", "Wi-Fi connectivity, corporate VPN, DNS resolution, LAN ports"),
            ("Access", "SSO credentials, Active Directory, role permissions, 2FA hardware keys"),
            ("Email", "Google Workspace / Outlook client issues, distribution lists, spam filter"),
            ("Security", "Phishing reports, suspicious logins, antivirus alerts, compliance"),
            ("Other", "General miscellaneous workplace technology assistance"),
        ]

        categories = []
        for name, desc in categories_data:
            cat = Category(name=name, description=desc, is_active=True)
            db.add(cat)
            categories.append(cat)
        db.commit()
        for c in categories:
            db.refresh(c)

        cat_dict = {c.name: c.id for c in categories}

        logger.info("Seeding 22 Realistic Tickets with Lifecycles and Comments...")
        now = datetime.now()

        # Seed realistic tickets with various timelines and statuses
        tickets_spec = [
            # OPEN Tickets
            {
                "title": "Dual external monitors not recognized via Thunderbolt dock",
                "desc": "Connecting my Dell XPS to the CalDigit USB-C dock only detects one display. The second monitor stays in power save mode.",
                "category": "Hardware",
                "priority": TicketPriority.MEDIUM,
                "status": TicketStatus.OPEN,
                "creator": emp1,
                "agent": None,
                "created_offset_h": 2,
            },
            {
                "title": "Cannot push to GitHub enterprise via Corporate VPN",
                "desc": "SSH connections to git.internal.org hang indefinitely when connected through WireGuard client on macOS.",
                "category": "Network",
                "priority": TicketPriority.HIGH,
                "status": TicketStatus.OPEN,
                "creator": emp2,
                "agent": None,
                "created_offset_h": 5,
            },
            {
                "title": "Access request for production PostgreSQL replica in read-only mode",
                "desc": "Need read-only credentials to troubleshoot customer billing discrepancies for Q3 data reconciliation.",
                "category": "Access",
                "priority": TicketPriority.LOW,
                "status": TicketStatus.OPEN,
                "creator": emp3,
                "agent": None,
                "created_offset_h": 1,
            },
            {
                "title": "Urgent: Phishing email campaign impersonating Org Payroll",
                "desc": "Received email from 'payroll-urgent@secure-hr-update.com' asking employees to re-enter direct deposit credentials.",
                "category": "Security",
                "priority": TicketPriority.CRITICAL,
                "status": TicketStatus.OPEN,
                "creator": emp4,
                "agent": None,
                "created_offset_h": 0.5,
            },

            # ASSIGNED Tickets
            {
                "title": "Docker Desktop licence expired on engineer workstation",
                "desc": "Local Docker engine stopped starting with error 'Business license required'. Need enterprise token applied.",
                "category": "Software",
                "priority": TicketPriority.MEDIUM,
                "status": TicketStatus.ASSIGNED,
                "creator": emp5,
                "agent": agent1,
                "created_offset_h": 8,
            },
            {
                "title": "Office 4th Floor North Wing Wi-Fi frequent disconnects",
                "desc": "Access point 4N-02 seems to drop packets every 10 minutes affecting video conferencing for the sales squad.",
                "category": "Network",
                "priority": TicketPriority.HIGH,
                "status": TicketStatus.ASSIGNED,
                "creator": emp1,
                "agent": agent2,
                "created_offset_h": 10,
            },
            {
                "title": "Slack enterprise SSO loop upon login",
                "desc": "Redirects from Okta back to login screen continuously without error message.",
                "category": "Access",
                "priority": TicketPriority.HIGH,
                "status": TicketStatus.ASSIGNED,
                "creator": emp2,
                "agent": agent1,
                "created_offset_h": 14,
            },

            # IN_PROGRESS Tickets
            {
                "title": "MacBook Pro keyboard typing double letters on spacebar",
                "desc": "Physical hardware issue on butterfly keyboard. Might need top case replacement or loaner laptop.",
                "category": "Hardware",
                "priority": TicketPriority.MEDIUM,
                "status": TicketStatus.IN_PROGRESS,
                "creator": emp3,
                "agent": agent2,
                "created_offset_h": 20,
            },
            {
                "title": "Customer support mailbox bouncebacks with code 550 SPF error",
                "desc": "Clients sending inquiries to support@company.com are getting delayed bouncebacks. DNS records need inspection.",
                "category": "Email",
                "priority": TicketPriority.CRITICAL,
                "status": TicketStatus.IN_PROGRESS,
                "creator": emp4,
                "agent": agent1,
                "created_offset_h": 3,
            },
            {
                "title": "AWS IAM permissions for Staging EKS cluster access",
                "desc": "Need kubernetes-admin role in AWS staging account to deploy microservices release v2.4.",
                "category": "Access",
                "priority": TicketPriority.MEDIUM,
                "status": TicketStatus.IN_PROGRESS,
                "creator": emp5,
                "agent": agent2,
                "created_offset_h": 18,
            },
            {
                "title": "IntelliJ IDEA Ultimate license key renewal",
                "desc": "JetBrains toolbox shows license expiring in 48 hours for engineering backend team.",
                "category": "Software",
                "priority": TicketPriority.LOW,
                "status": TicketStatus.IN_PROGRESS,
                "creator": emp1,
                "agent": agent1,
                "created_offset_h": 26,
            },

            # RESOLVED Tickets
            {
                "title": "Zoom client camera rendering black screen on Windows 11",
                "desc": "Integrated webcam works in Camera app but Zoom renders black screen during standup calls.",
                "category": "Software",
                "priority": TicketPriority.MEDIUM,
                "status": TicketStatus.RESOLVED,
                "creator": emp2,
                "agent": agent1,
                "created_offset_h": 36,
                "resolved_offset_h": 6,
                "res_notes": "Updated Intel integrated graphics driver to v31.0 and granted Zoom privacy permissions under Windows 11 settings.",
            },
            {
                "title": "VPN certificate expired for remote contractor setup",
                "desc": "Contractor Alice cannot connect to staging VPN profile due to expired SSL cert.",
                "category": "Network",
                "priority": TicketPriority.HIGH,
                "status": TicketStatus.RESOLVED,
                "creator": emp3,
                "agent": agent2,
                "created_offset_h": 24,
                "resolved_offset_h": 2,
                "res_notes": "Generated fresh client TLS certificate and delivered securely via 1Password vault.",
            },
            {
                "title": "YubiKey 5C NFC hardware security key replacement",
                "desc": "Lost physical 2FA hardware key during transit. Temporarily using SMS auth but company policy requires hardware token.",
                "category": "Security",
                "priority": TicketPriority.HIGH,
                "status": TicketStatus.RESOLVED,
                "creator": emp4,
                "agent": agent1,
                "created_offset_h": 30,
                "resolved_offset_h": 4,
                "res_notes": "Revoked lost key ID from Okta Directory, issued new configured YubiKey at IT helpdesk.",
            },
            {
                "title": "Figma Enterprise seat invite not received",
                "desc": "Joined product design chapter this Monday. Need editor permissions on core design system files.",
                "category": "Access",
                "priority": TicketPriority.LOW,
                "status": TicketStatus.RESOLVED,
                "creator": emp5,
                "agent": agent2,
                "created_offset_h": 40,
                "resolved_offset_h": 12,
                "res_notes": "Approved by manager and added user to the Figma Organization Team as full editor.",
            },

            # CLOSED Tickets
            {
                "title": "New hire onboarding hardware kit delivery",
                "desc": "Requesting standard M3 MacBook Pro 36GB, Dell 27 4K display, and wireless magic mouse.",
                "category": "Hardware",
                "priority": TicketPriority.MEDIUM,
                "status": TicketStatus.CLOSED,
                "creator": emp1,
                "agent": agent2,
                "created_offset_h": 80,
                "resolved_offset_h": 50,
                "closed_offset_h": 40,
                "res_notes": "Hardware prepared, MDM profile enrolled, kit signed off and collected by employee.",
            },
            {
                "title": "Configure automated email forwarding to team alias",
                "desc": "Route incoming emails from client-success@ to the Zendesk shared inbox.",
                "category": "Email",
                "priority": TicketPriority.LOW,
                "status": TicketStatus.CLOSED,
                "creator": emp2,
                "agent": agent1,
                "created_offset_h": 100,
                "resolved_offset_h": 70,
                "closed_offset_h": 60,
                "res_notes": "Configured Google Workspace routing rule with DKIM preservation enabled.",
            },
            {
                "title": "Database connection pool exhaustion on Dev MySQL",
                "desc": "Dev instance hanging with error Too Many Connections after stress testing script.",
                "category": "Other",
                "priority": TicketPriority.HIGH,
                "status": TicketStatus.CLOSED,
                "creator": emp3,
                "agent": agent2,
                "created_offset_h": 90,
                "resolved_offset_h": 85,
                "closed_offset_h": 80,
                "res_notes": "Killed dormant client connections, increased max_connections to 300, and optimized connection pool recycling.",
            },

            # REOPENED Ticket (Demonstrates Section 3 & 11)
            {
                "title": "Printer on 2nd Floor keeps jamming on double-sided printing",
                "desc": "HP LaserJet MFP M528 reported as fixed yesterday, but jammed again on tray 2 duplex paper feed.",
                "category": "Hardware",
                "priority": TicketPriority.MEDIUM,
                "status": TicketStatus.REOPENED,
                "creator": emp4,
                "agent": agent1,
                "created_offset_h": 48,
                "resolved_offset_h": 20,
                "res_notes": "Cleared paper jam on tray 2 and tested single page output.",
            },

            # SLA Breached Tickets (for testing KPI and dashboard breach indicators)
            {
                "title": "Core Router Switch B failing over repeatedly",
                "desc": "Network core rack 4 switch dropping BGP peers causing cross-rack latency spikes.",
                "category": "Network",
                "priority": TicketPriority.CRITICAL,
                "status": TicketStatus.IN_PROGRESS,
                "creator": emp5,
                "agent": agent2,
                "created_offset_h": 12, # Critical SLA is 4 hours, so 12 hours ago means breached!
            },
            {
                "title": "PostgreSQL data warehouse nightly ETL pipeline timeout",
                "desc": "Nightly Airflow dag timing out after 6 hours due to missing index on fact_events table.",
                "category": "Software",
                "priority": TicketPriority.HIGH,
                "status": TicketStatus.OPEN,
                "creator": emp1,
                "agent": None,
                "created_offset_h": 30, # High SLA is 24 hours, so 30 hours ago means breached!
            },
            {
                "title": "VPN connection drops every time laptop sleeps",
                "desc": "OpenVPN TAP adapter fails to renegotiate handshake upon waking from sleep.",
                "category": "Network",
                "priority": TicketPriority.LOW,
                "status": TicketStatus.OPEN,
                "creator": emp2,
                "agent": None,
                "created_offset_h": 85, # Low SLA is 72 hours, so 85 hours ago means breached!
            },
        ]

        for spec in tickets_spec:
            created_at = now - timedelta(hours=spec["created_offset_h"])
            due_at = SLAService.calculate_due_date(created_at, spec["priority"])

            resolved_at = None
            if "resolved_offset_h" in spec:
                resolved_at = now - timedelta(hours=spec["resolved_offset_h"])

            closed_at = None
            if "closed_offset_h" in spec:
                closed_at = now - timedelta(hours=spec["closed_offset_h"])

            ticket = Ticket(
                title=spec["title"],
                description=spec["desc"],
                category_id=cat_dict[spec["category"]],
                priority=spec["priority"],
                status=spec["status"],
                created_by=spec["creator"].id,
                assigned_to=spec["agent"].id if spec["agent"] else None,
                created_at=created_at,
                updated_at=now,
                due_at=due_at,
                resolved_at=resolved_at,
                closed_at=closed_at,
                resolution_notes=spec.get("res_notes"),
            )
            db.add(ticket)
            db.commit()
            db.refresh(ticket)

            # Record initial history
            h1 = TicketStatusHistory(
                ticket_id=ticket.id,
                old_status=None,
                new_status=TicketStatus.OPEN,
                changed_by=spec["creator"].id,
                changed_at=created_at,
            )
            db.add(h1)

            # If assigned
            if spec["agent"]:
                h2 = TicketStatusHistory(
                    ticket_id=ticket.id,
                    old_status=TicketStatus.OPEN,
                    new_status=TicketStatus.ASSIGNED,
                    changed_by=admin.id,
                    changed_at=created_at + timedelta(minutes=15),
                )
                db.add(h2)

            # If in progress
            if spec["status"] in [TicketStatus.IN_PROGRESS, TicketStatus.RESOLVED, TicketStatus.CLOSED, TicketStatus.REOPENED]:
                h3 = TicketStatusHistory(
                    ticket_id=ticket.id,
                    old_status=TicketStatus.ASSIGNED,
                    new_status=TicketStatus.IN_PROGRESS,
                    changed_by=spec["agent"].id if spec["agent"] else admin.id,
                    changed_at=created_at + timedelta(hours=1),
                )
                db.add(h3)

            # If resolved
            if resolved_at:
                h4 = TicketStatusHistory(
                    ticket_id=ticket.id,
                    old_status=TicketStatus.IN_PROGRESS,
                    new_status=TicketStatus.RESOLVED,
                    changed_by=spec["agent"].id if spec["agent"] else admin.id,
                    changed_at=resolved_at,
                )
                db.add(h4)

            # If closed
            if closed_at:
                h5 = TicketStatusHistory(
                    ticket_id=ticket.id,
                    old_status=TicketStatus.RESOLVED,
                    new_status=TicketStatus.CLOSED,
                    changed_by=admin.id,
                    changed_at=closed_at,
                )
                db.add(h5)

            # If reopened
            if spec["status"] == TicketStatus.REOPENED:
                h6 = TicketStatusHistory(
                    ticket_id=ticket.id,
                    old_status=TicketStatus.RESOLVED,
                    new_status=TicketStatus.REOPENED,
                    changed_by=spec["creator"].id,
                    changed_at=now - timedelta(hours=2),
                )
                db.add(h6)

            # Add sample comments
            c1 = Comment(
                ticket_id=ticket.id,
                user_id=spec["creator"].id,
                comment=f"Reporting this issue: {spec['title']}. Please let me know if diagnostic logs are required.",
                created_at=created_at + timedelta(minutes=5),
            )
            db.add(c1)

            if spec["agent"]:
                c2 = Comment(
                    ticket_id=ticket.id,
                    user_id=spec["agent"].id,
                    comment="Acknowledged. Reviewing telemetry and configurations to isolate root cause.",
                    created_at=created_at + timedelta(minutes=25),
                )
                db.add(c2)

            if spec.get("res_notes"):
                c3 = Comment(
                    ticket_id=ticket.id,
                    user_id=spec["agent"].id if spec["agent"] else admin.id,
                    comment=f"Resolution Applied: {spec['res_notes']}",
                    created_at=resolved_at or (now - timedelta(hours=1)),
                )
                db.add(c3)

            # Audit log
            audit = AuditLog(
                user_id=spec["creator"].id,
                action="TICKET_SEEDED",
                entity_type="TICKET",
                entity_id=ticket.id,
            )
            db.add(audit)

        db.commit()
        logger.info("Successfully seeded database with 8 users, 7 categories, and 22 tickets!")

    except Exception as e:
        logger.exception(f"Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()

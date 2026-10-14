import os
import sys
import argparse
from sqlalchemy.orm import Session

# Ensure backend package can be imported
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database.connection import engine
from app.database.session import SessionLocal
from app.database.base import Base
from app.models.ticket import Ticket
from app.models.comment import Comment
from app.models.status_history import TicketStatusHistory
from app.models.audit import AuditLog
from app.models.user import User, UserRole
from app.models.category import Category
from app.core.security import get_password_hash
from app.core.logging import logger


def clear_sample_data(keep_core_users: bool = True):
    """
    Cleans sample data from the database.
    - Removes all tickets, comments, status histories, and audit logs.
    - If keep_core_users is True, preserves the 3 demo role accounts:
      Admin (admin@trackit.internal), Agent (agent.sarah@trackit.internal),
      and Employee (emp.alice@trackit.internal), plus the 7 standard categories.
    """
    db: Session = SessionLocal()
    try:
        logger.info("Cleaning sample data from TrackIT database...")

        # 1. Delete comments and status history
        deleted_comments = db.query(Comment).delete()
        deleted_history = db.query(TicketStatusHistory).delete()
        logger.info(f"Deleted {deleted_comments} comments and {deleted_history} status history records.")

        # 2. Delete tickets
        deleted_tickets = db.query(Ticket).delete()
        logger.info(f"Deleted {deleted_tickets} tickets.")

        # 3. Delete audit logs
        deleted_audits = db.query(AuditLog).delete()
        logger.info(f"Deleted {deleted_audits} audit log entries.")

        # 4. Handle Users
        if keep_core_users:
            core_emails = [
                "admin@trackit.internal",
                "agent.sarah@trackit.internal",
                "emp.alice@trackit.internal",
            ]
            # Remove any users that are not the 3 core demo users
            deleted_users = db.query(User).filter(~User.email.in_(core_emails)).delete(synchronize_session=False)
            logger.info(f"Removed {deleted_users} extraneous sample users. Retained 3 core demo accounts.")

            # Ensure the 3 core demo accounts exist
            admin = db.query(User).filter(User.email == "admin@trackit.internal").first()
            if not admin:
                db.add(User(
                    name="Alexander Mitchell",
                    email="admin@trackit.internal",
                    password_hash=get_password_hash("Admin@123"),
                    role=UserRole.ADMIN,
                    is_active=True,
                ))

            agent = db.query(User).filter(User.email == "agent.sarah@trackit.internal").first()
            if not agent:
                db.add(User(
                    name="Sarah Jenkins",
                    email="agent.sarah@trackit.internal",
                    password_hash=get_password_hash("Agent@123"),
                    role=UserRole.SUPPORT_AGENT,
                    is_active=True,
                ))

            emp = db.query(User).filter(User.email == "emp.alice@trackit.internal").first()
            if not emp:
                db.add(User(
                    name="Alice Morgan",
                    email="emp.alice@trackit.internal",
                    password_hash=get_password_hash("Employee@123"),
                    role=UserRole.EMPLOYEE,
                    is_active=True,
                ))
        else:
            deleted_users = db.query(User).delete()
            logger.info(f"Deleted all {deleted_users} users.")

        # 5. Ensure standard Categories exist
        categories_data = [
            ("Hardware", "Physical computing equipment: laptops, monitors, docking stations, peripherals"),
            ("Software", "Licensed enterprise applications, developer tooling, OS installations"),
            ("Network", "Wi-Fi connectivity, corporate VPN, DNS resolution, LAN ports"),
            ("Access", "SSO credentials, Active Directory, role permissions, 2FA hardware keys"),
            ("Email", "Google Workspace / Outlook client issues, distribution lists, spam filter"),
            ("Security", "Phishing reports, suspicious logins, antivirus alerts, compliance"),
            ("Other", "General miscellaneous workplace technology assistance"),
        ]
        for name, desc in categories_data:
            existing_cat = db.query(Category).filter(Category.name == name).first()
            if not existing_cat:
                db.add(Category(name=name, description=desc, is_active=True))

        db.commit()

        # Log completion audit
        logger.info("Successfully cleaned database! Ready for real user tickets.")
        print("\n" + "=" * 60)
        print(" [SUCCESS] SAMPLE DATA REMOVED SUCCESSFULLY")
        print("=" * 60)
        print(f" Tickets removed:         {deleted_tickets}")
        print(f" Comments removed:        {deleted_comments}")
        print(f" Status records removed:  {deleted_history}")
        print(f" Audit records removed:   {deleted_audits}")
        print("-" * 60)
        print(" Active Clean State:")
        print(" - Tickets:    0 (Ready for real tickets)")
        print(" - Categories: 7 Standard categories available")
        print(" - Core Users:")
        print("   * Admin:    admin@trackit.internal       / Admin@123")
        print("   * Agent:    agent.sarah@trackit.internal / Agent@123")
        print("   * Employee: emp.alice@trackit.internal   / Employee@123")
        print("=" * 60 + "\n")

    except Exception as e:
        db.rollback()
        logger.error(f"Error during sample data cleaning: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clean TrackIT sample data")
    parser.add_argument(
        "--purge-all-users",
        action="store_true",
        help="Purge all users including demo accounts (Admin/Agent/Employee)",
    )
    args = parser.parse_args()
    clear_sample_data(keep_core_users=not args.purge_all_users)

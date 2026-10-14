import os
import sys
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database.base import Base
from app.database.session import get_db
from app.main import app
from app.core.security import get_password_hash, create_access_token
from app.models.user import User, UserRole
from app.models.category import Category
from app.models.ticket import Ticket, TicketStatus, TicketPriority

TEST_DATABASE_URL = "sqlite:///./test_trackit.db"
test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)
    if os.path.exists("./test_trackit.db"):
        try:
            os.remove("./test_trackit.db")
        except Exception:
            pass


@pytest.fixture
def db_session():
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_category(db_session):
    cat = Category(name="Network Issues", description="Wi-Fi, VPN and routing", is_active=True)
    db_session.add(cat)
    db_session.commit()
    db_session.refresh(cat)
    return cat


@pytest.fixture
def admin_user(db_session):
    user = User(
        name="Admin Test",
        email="test.admin@trackit.internal",
        password_hash=get_password_hash("Password@123"),
        role=UserRole.ADMIN,
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def agent_user(db_session):
    user = User(
        name="Agent Test",
        email="test.agent@trackit.internal",
        password_hash=get_password_hash("Password@123"),
        role=UserRole.SUPPORT_AGENT,
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def employee_user(db_session):
    user = User(
        name="Employee One",
        email="test.emp1@trackit.internal",
        password_hash=get_password_hash("Password@123"),
        role=UserRole.EMPLOYEE,
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def employee_user_2(db_session):
    user = User(
        name="Employee Two",
        email="test.emp2@trackit.internal",
        password_hash=get_password_hash("Password@123"),
        role=UserRole.EMPLOYEE,
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def get_token_header(user: User) -> dict:
    token = create_access_token(data={"sub": str(user.id), "email": user.email, "role": user.role, "name": user.name})
    return {"Authorization": f"Bearer {token}"}

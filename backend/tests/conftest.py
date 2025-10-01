import pytest
import asyncio
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.database import get_db
from app.models.base import Base
from app.models.user import User
from app.models.client import Client
from app.models.asset import Asset
from app.core.security import get_password_hash, create_access_token

# Use SQLite for tests (synchronous)
TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
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
def test_user(db_session):
    user = User(
        email="test@example.com",
        password=get_password_hash("testpassword"),
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def auth_token(test_user):
    return create_access_token(data={"sub": test_user.email})

@pytest.fixture
def auth_headers(auth_token):
    return {"Authorization": f"Bearer {auth_token}"}

@pytest.fixture
def test_client_model(db_session):
    client = Client(
        name="Test Client",
        email="client@example.com",
        is_active=True
    )
    db_session.add(client)
    db_session.commit()
    db_session.refresh(client)
    return client

@pytest.fixture
def test_asset(db_session):
    asset = Asset(
        ticker="AAPL",
        name="Apple Inc.",
        exchange="NASDAQ",
        currency="USD"
    )
    db_session.add(asset)
    db_session.commit()
    db_session.refresh(asset)
    return asset
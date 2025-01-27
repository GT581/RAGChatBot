import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from app.db.database import Base, get_db
from app.main import app
from app.core.settings import settings
import os

# Test database URL
SQLALCHEMY_TEST_DATABASE_URL = settings.sync_database_url.replace(
    settings.POSTGRES_DB, 
    f"test_{settings.POSTGRES_DB}"
)

# Create test engine
engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL)

# Create test session
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
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
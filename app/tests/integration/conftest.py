import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from database.database import Base
from main import app, get_db

# StaticPool garante que todas as conexões usem o mesmo banco in-memory,
# evitando que cada nova conexão abra um banco vazio.
engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = override_get_db
    yield
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def user_payload():
    return {
        "name": "Arthur",
        "password": "secret",
        "budget_ceiling": 2000,
        "incomes": [{"name": "Salário", "income_value": 5000}],
        "expenses": [{"name": "Notebook", "expense_value": 3000, "installment": 10}],
        "bills": [{"name": "Aluguel", "bill_value": 1200}],
        "investments": [{"name": "Tesouro Direto", "value_invested": 10000, "dividends": 500}],
    }

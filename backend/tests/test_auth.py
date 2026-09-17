import uuid
from datetime import UTC, datetime

from fastapi.testclient import TestClient

from backend.db.database import get_session
from backend.db.models.user import User
from backend.main import app


class FakeSession:
    def __init__(self, user: User | None = None) -> None:
        self.user = user
        self.created: User | None = None

    async def scalar(self, statement):
        return self.user

    async def get(self, model, key):
        return self.user if self.user and self.user.id == key else None

    def add(self, user: User) -> None:
        self.created = user

    async def commit(self) -> None:
        pass

    async def refresh(self, user: User) -> None:
        user.id = uuid.uuid4()
        user.is_active = True
        now = datetime.now(UTC)
        user.created_at = now
        user.updated_at = now


def override_session(session: FakeSession):
    async def dependency():
        yield session

    app.dependency_overrides[get_session] = dependency


def test_register_creates_user_without_password_hash_in_response() -> None:
    session = FakeSession()
    override_session(session)

    response = TestClient(app).post(
        "/api/v1/auth/register",
        json={"email": "a@example.com", "password": "password123", "name": "A User", "role": "employee"},
    )

    app.dependency_overrides.clear()
    assert response.status_code == 201
    assert "password" not in response.text
    assert session.created is not None
    assert session.created.password_hash != "password123"


def test_login_returns_token() -> None:
    from backend.core.security import hash_password

    user = User(
        id=uuid.uuid4(),
        email="a@example.com",
        password_hash=hash_password("password123"),
        name="A User",
        role="employee",
        is_active=True,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    override_session(FakeSession(user))

    response = TestClient(app).post("/api/v1/auth/login", json={"email": user.email, "password": "password123"})

    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert response.json()["access_token"]


def test_me_requires_valid_token() -> None:
    from backend.core.security import create_access_token

    user = User(
        id=uuid.uuid4(),
        email="a@example.com",
        password_hash="x",
        name="A User",
        role="employee",
        is_active=True,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    override_session(FakeSession(user))

    response = TestClient(app).get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {create_access_token(str(user.id))}"},
    )

    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()["email"] == user.email

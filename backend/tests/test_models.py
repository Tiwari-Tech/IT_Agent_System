import uuid
from pathlib import Path

from sqlalchemy.orm import configure_mappers

from backend.db.base import Base
from backend.db.models import AgentRun, AuditLog, Document, Message, Ticket, User


def test_metadata_has_expected_tables() -> None:
    assert set(Base.metadata.tables) == {
        "agent_runs",
        "audit_logs",
        "documents",
        "messages",
        "tickets",
        "users",
    }


def test_uuid_primary_key_defaults() -> None:
    for model in (AgentRun, AuditLog, Document, Message, Ticket, User):
        column = model.__table__.c.id
        assert column.primary_key
        assert column.default is not None
        assert isinstance(column.default.arg(None), uuid.UUID)


def test_relationships_configure() -> None:
    configure_mappers()

    assert User.created_tickets.property.mapper.class_ is Ticket
    assert User.assigned_tickets.property.mapper.class_ is Ticket
    assert Ticket.creator.property.mapper.class_ is User
    assert Ticket.assignee.property.mapper.class_ is User
    assert Ticket.agent_runs.property.mapper.class_ is AgentRun
    assert Ticket.messages.property.mapper.class_ is Message
    assert Message.user.property.mapper.class_ is User
    assert AuditLog.user.property.mapper.class_ is User


def test_indexes_and_constraints_exist() -> None:
    assert User.__table__.c.email.unique is True
    assert {index.name for index in Ticket.__table__.indexes} == {
        "ix_tickets_created_at",
        "ix_tickets_priority",
        "ix_tickets_status",
    }
    assert {index.name for index in Document.__table__.indexes} == {"ix_documents_content_hash"}


def test_alembic_metadata_imports_models() -> None:
    env_py = Path(__file__).resolve().parents[1] / "alembic" / "env.py"
    content = env_py.read_text()

    assert "from backend.db.base import Base" in content
    assert "from backend.db import models" in content
    assert "target_metadata = Base.metadata" in content

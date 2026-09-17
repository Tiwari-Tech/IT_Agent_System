import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models.audit_log import AuditLog
from backend.db.models.message import Message
from backend.db.models.ticket import Ticket
from backend.db.models.user import User
from backend.repositories.tickets import (
    add_audit_log,
    add_message,
    create_ticket,
    get_ticket,
    list_tickets,
)
from backend.schemas.ticket import MessageCreate, TicketCreate, TicketUpdate

STATUSES = {"open", "in_progress", "resolved", "closed"}
PRIORITIES = {"low", "medium", "high", "critical"}


def validate_status_priority(status_value: str | None, priority: str | None) -> None:
    if status_value is not None and status_value not in STATUSES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid status")
    if priority is not None and priority not in PRIORITIES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid priority")


def can_view(user: User, ticket: Ticket) -> bool:
    return user.role in {"it_support", "it_admin"} or ticket.created_by == user.id or ticket.assigned_to == user.id


async def create_user_ticket(session: AsyncSession, user: User, payload: TicketCreate) -> Ticket:
    validate_status_priority(payload.status, payload.priority)
    return await create_ticket(
        session,
        Ticket(
            title=payload.title,
            description=payload.description,
            status=payload.status,
            priority=payload.priority,
            category=payload.category,
            created_by=user.id,
        ),
    )


async def find_ticket(session: AsyncSession, user: User, ticket_id: uuid.UUID) -> Ticket:
    ticket = await get_ticket(session, ticket_id)
    if ticket is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
    if not can_view(user, ticket):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role")
    return ticket


async def search_tickets(
    session: AsyncSession,
    user: User,
    *,
    page: int,
    limit: int,
    status_value: str | None,
    priority: str | None,
    category: str | None,
) -> tuple[list[Ticket], int]:
    validate_status_priority(status_value, priority)
    return await list_tickets(
        session,
        page=page,
        limit=limit,
        status=status_value,
        priority=priority,
        category=category,
        user_id=None if user.role in {"it_support", "it_admin"} else user.id,
    )


async def update_ticket(session: AsyncSession, user: User, ticket_id: uuid.UUID, payload: TicketUpdate) -> Ticket:
    ticket = await find_ticket(session, user, ticket_id)
    data = payload.model_dump(exclude_unset=True)
    validate_status_priority(data.get("status"), data.get("priority"))

    support_fields = {"status", "priority", "category", "assigned_to"}
    if user.role == "employee" and (ticket.created_by != user.id or support_fields & data.keys()):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role")

    changes = {key: {"old": str(getattr(ticket, key)), "new": str(value)} for key, value in data.items() if getattr(ticket, key) != value}
    for key, value in data.items():
        setattr(ticket, key, value)
    if changes:
        await add_audit_log(
            session,
            AuditLog(user_id=user.id, action="ticket.updated", resource_type="ticket", resource_id=str(ticket.id), details=changes),
        )
    await session.commit()
    return await find_ticket(session, user, ticket.id)


async def create_message(session: AsyncSession, user: User, ticket_id: uuid.UUID, payload: MessageCreate) -> Message:
    ticket = await find_ticket(session, user, ticket_id)
    return await add_message(session, Message(ticket_id=ticket.id, user_id=user.id, role=user.role, content=payload.content))

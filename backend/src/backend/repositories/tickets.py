import uuid

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.db.models.audit_log import AuditLog
from backend.db.models.message import Message
from backend.db.models.ticket import Ticket


def ticket_options():
    return selectinload(Ticket.creator), selectinload(Ticket.assignee)


async def create_ticket(session: AsyncSession, ticket: Ticket) -> Ticket:
    session.add(ticket)
    await session.commit()
    return await get_ticket(session, ticket.id) or ticket


async def get_ticket(session: AsyncSession, ticket_id: uuid.UUID) -> Ticket | None:
    return await session.scalar(select(Ticket).options(*ticket_options()).where(Ticket.id == ticket_id))


async def list_tickets(
    session: AsyncSession,
    *,
    page: int,
    limit: int,
    status: str | None,
    priority: str | None,
    category: str | None,
    user_id: uuid.UUID | None = None,
) -> tuple[list[Ticket], int]:
    filters = []
    if status:
        filters.append(Ticket.status == status)
    if priority:
        filters.append(Ticket.priority == priority)
    if category:
        filters.append(Ticket.category == category)
    if user_id:
        filters.append(or_(Ticket.created_by == user_id, Ticket.assigned_to == user_id))

    query = select(Ticket).options(*ticket_options()).where(*filters).order_by(Ticket.created_at.desc())
    total = await session.scalar(select(func.count()).select_from(Ticket).where(*filters))
    rows = await session.scalars(query.offset((page - 1) * limit).limit(limit))
    return list(rows), int(total or 0)


async def add_message(session: AsyncSession, message: Message) -> Message:
    session.add(message)
    await session.commit()
    await session.refresh(message)
    return message


async def add_audit_log(session: AsyncSession, log: AuditLog) -> None:
    session.add(log)

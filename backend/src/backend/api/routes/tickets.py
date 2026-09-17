import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.dependencies.auth import get_current_user
from backend.db.database import get_session
from backend.db.models.user import User
from backend.schemas.ticket import (
    MessageCreate,
    MessageResponse,
    TicketCreate,
    TicketListResponse,
    TicketResponse,
    TicketUpdate,
)
from backend.services.tickets import (
    create_message,
    create_user_ticket,
    find_ticket,
    search_tickets,
    update_ticket,
)

router = APIRouter(prefix="/api/v1/tickets", tags=["tickets"])


@router.post("", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
async def create_ticket(payload: TicketCreate, user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    return await create_user_ticket(session, user, payload)


@router.get("", response_model=TicketListResponse)
async def list_tickets(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status: str | None = None,
    priority: str | None = None,
    category: str | None = None,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
) -> TicketListResponse:
    items, total = await search_tickets(session, user, page=page, limit=limit, status_value=status, priority=priority, category=category)
    return TicketListResponse(items=items, total=total, page=page, limit=limit)


@router.get("/{ticket_id}", response_model=TicketResponse)
async def get_ticket(ticket_id: uuid.UUID, user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    return await find_ticket(session, user, ticket_id)


@router.patch("/{ticket_id}", response_model=TicketResponse)
async def patch_ticket(ticket_id: uuid.UUID, payload: TicketUpdate, user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    return await update_ticket(session, user, ticket_id, payload)


@router.post("/{ticket_id}/messages", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def post_message(ticket_id: uuid.UUID, payload: MessageCreate, user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    return await create_message(session, user, ticket_id, payload)

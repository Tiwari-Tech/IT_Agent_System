import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from backend.schemas.user import UserSafe


class TicketCreate(BaseModel):
    title: str = Field(min_length=1, max_length=500)
    description: str = Field(min_length=1)
    status: str = "open"
    priority: str = "medium"
    category: str | None = None


class TicketUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=500)
    description: str | None = Field(default=None, min_length=1)
    status: str | None = None
    priority: str | None = None
    category: str | None = None
    assigned_to: uuid.UUID | None = None


class MessageCreate(BaseModel):
    content: str = Field(min_length=1)


class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    ticket_id: uuid.UUID | None
    user_id: uuid.UUID | None
    role: str
    content: str
    created_at: datetime


class TicketResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    external_ticket_id: str | None
    title: str
    description: str
    status: str
    priority: str
    category: str | None
    created_by: uuid.UUID
    assigned_to: uuid.UUID | None
    created_at: datetime
    updated_at: datetime
    creator: UserSafe
    assignee: UserSafe | None


class TicketListResponse(BaseModel):
    items: list[TicketResponse]
    total: int
    page: int
    limit: int

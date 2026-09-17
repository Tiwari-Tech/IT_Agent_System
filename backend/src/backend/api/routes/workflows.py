import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.dependencies.auth import get_current_user
from backend.db.database import get_session
from backend.db.models.user import User
from backend.schemas.workflow import WorkflowRunResponse
from backend.services.workflows import run_workflow_for_ticket

router = APIRouter(prefix="/api/v1/workflows", tags=["workflows"])


@router.post("/tickets/{ticket_id}/run", response_model=WorkflowRunResponse)
async def run_ticket_workflow_endpoint(
    ticket_id: uuid.UUID,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> WorkflowRunResponse:
    return await run_workflow_for_ticket(session, ticket_id, user)

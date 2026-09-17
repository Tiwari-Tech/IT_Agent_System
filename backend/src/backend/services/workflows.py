import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.agents.workflow import run_ticket_workflow
from backend.db.models.ticket import Ticket
from backend.db.models.user import User
from backend.schemas.workflow import WorkflowRunResponse
from backend.services.tickets import can_view


async def run_workflow_for_ticket(session: AsyncSession, ticket_id: uuid.UUID, user: User | None = None) -> WorkflowRunResponse:
    ticket = await session.get(Ticket, ticket_id)
    if ticket is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
    if user is not None and not can_view(user, ticket):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role")

    state = await run_ticket_workflow(session, ticket, user.id if user else None)
    ticket.status = "in_progress" if state.get("requires_human_approval") else "resolved"
    await session.commit()
    return WorkflowRunResponse(
        ticket_id=ticket.id,
        workflow_id=state["workflow_id"],
        status=ticket.status,
        requires_human_approval=state.get("requires_human_approval", False),
        review_result=state.get("review_result"),
        resolution_plan=state.get("resolution_plan"),
        jira_issue_key=ticket.external_ticket_id,
        agent_run_ids=state.get("agent_run_ids", []),
        errors=state.get("errors", []),
        state=dict(state),
    )

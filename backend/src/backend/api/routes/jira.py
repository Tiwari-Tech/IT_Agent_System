import uuid
from collections.abc import Awaitable, Callable
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.dependencies.auth import require_role
from backend.db.database import get_session
from backend.db.models.ticket import Ticket
from backend.db.models.user import User
from backend.integrations.jira.client import JiraClient, JiraError
from backend.integrations.jira.service import audit_jira, sync_status
from backend.schemas.jira import (
    JiraCommentCreate,
    JiraIssueCreate,
    JiraIssueUpdate,
    JiraResponse,
    JiraStatusSync,
)

router = APIRouter(prefix="/api/v1/jira", tags=["jira"])


async def safe_jira(call: Callable[[], Awaitable[dict[str, Any]]]) -> dict[str, Any]:
    try:
        return await call()
    except JiraError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Jira unavailable") from exc


@router.post("/issues", response_model=JiraResponse)
async def create_issue(payload: JiraIssueCreate, _: User = Depends(require_role("it_support", "it_admin"))) -> JiraResponse:
    return JiraResponse(data=await safe_jira(lambda: JiraClient().create_issue(summary=payload.summary, description=payload.description, issue_type=payload.issue_type)))


@router.get("/issues/{issue_key}", response_model=JiraResponse)
async def get_issue(issue_key: str, _: User = Depends(require_role("it_support", "it_admin"))) -> JiraResponse:
    return JiraResponse(data=await safe_jira(lambda: JiraClient().get_issue(issue_key)))


@router.patch("/issues/{issue_key}", response_model=JiraResponse)
async def update_issue(issue_key: str, payload: JiraIssueUpdate, _: User = Depends(require_role("it_support", "it_admin"))) -> JiraResponse:
    return JiraResponse(data=await safe_jira(lambda: JiraClient().update_issue(issue_key, payload.fields)))


@router.post("/issues/{issue_key}/comments", response_model=JiraResponse)
async def add_comment(issue_key: str, payload: JiraCommentCreate, _: User = Depends(require_role("it_support", "it_admin"))) -> JiraResponse:
    return JiraResponse(data=await safe_jira(lambda: JiraClient().add_comment(issue_key, payload.body)))


@router.post("/tickets/{ticket_id}/sync-status", response_model=dict[str, bool])
async def sync_ticket_status(
    ticket_id: uuid.UUID,
    payload: JiraStatusSync,
    _: User = Depends(require_role("it_support", "it_admin")),
    session: AsyncSession = Depends(get_session),
) -> dict[str, bool]:
    ticket = await session.get(Ticket, ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
    ok = await sync_status(session, ticket, payload.transition_id)
    if ok:
        await audit_jira(session, ticket, "jira.manual_status_sync", {"issue_key": ticket.external_ticket_id})
    return {"ok": ok}

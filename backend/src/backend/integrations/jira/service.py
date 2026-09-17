from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models.audit_log import AuditLog
from backend.db.models.ticket import Ticket
from backend.integrations.jira.client import JiraClient, JiraError


async def audit_jira(session: AsyncSession, ticket: Ticket, action: str, details: dict[str, Any]) -> None:
    session.add(AuditLog(user_id=None, action=action, resource_type="ticket", resource_id=str(ticket.id), details=details))
    await session.commit()


async def create_or_sync_issue(session: AsyncSession, ticket: Ticket, comment: str | None = None) -> str | None:
    client = JiraClient()
    if not client.configured:
        return None
    try:
        if not ticket.external_ticket_id:
            issue = await client.create_issue(summary=ticket.title, description=ticket.description)
            ticket.external_ticket_id = issue.get("key")
            await audit_jira(session, ticket, "jira.issue_created", {"issue_key": ticket.external_ticket_id})
        if ticket.external_ticket_id and comment:
            await client.add_comment(ticket.external_ticket_id, comment[:30000])
            await audit_jira(session, ticket, "jira.comment_added", {"issue_key": ticket.external_ticket_id})
        await session.commit()
        return ticket.external_ticket_id
    except JiraError:
        await audit_jira(session, ticket, "jira.sync_failed", {"issue_key": ticket.external_ticket_id})
        return None


async def sync_status(session: AsyncSession, ticket: Ticket, transition_id: str) -> bool:
    if not ticket.external_ticket_id:
        return False
    try:
        await JiraClient().transition_issue(ticket.external_ticket_id, transition_id)
        await audit_jira(session, ticket, "jira.status_synced", {"issue_key": ticket.external_ticket_id, "transition_id": transition_id})
        return True
    except JiraError:
        await audit_jira(session, ticket, "jira.sync_failed", {"issue_key": ticket.external_ticket_id})
        return False

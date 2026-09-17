import uuid
from typing import Any

from pydantic import BaseModel


class WorkflowRunResponse(BaseModel):
    ticket_id: uuid.UUID
    workflow_id: str
    status: str
    requires_human_approval: bool
    review_result: str | None = None
    resolution_plan: str | None = None
    jira_issue_key: str | None = None
    agent_run_ids: list[str]
    errors: list[str]
    state: dict[str, Any]

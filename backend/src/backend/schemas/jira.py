from typing import Any

from pydantic import BaseModel


class JiraIssueCreate(BaseModel):
    summary: str
    description: str
    issue_type: str = "Task"


class JiraIssueUpdate(BaseModel):
    fields: dict[str, Any]


class JiraCommentCreate(BaseModel):
    body: str


class JiraStatusSync(BaseModel):
    transition_id: str


class JiraResponse(BaseModel):
    data: dict[str, Any]

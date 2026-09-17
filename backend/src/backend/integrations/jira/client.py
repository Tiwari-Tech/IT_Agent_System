from typing import Any

import httpx

from backend.core.config import get_settings


class JiraError(RuntimeError):
    pass


class JiraClient:
    def __init__(self) -> None:
        settings = get_settings()
        self.base_url = settings.jira_base_url.rstrip("/")
        self.project_key = settings.jira_project_key
        self.auth = (settings.jira_email, settings.jira_api_token)
        self.timeout = settings.jira_timeout_seconds

    @property
    def configured(self) -> bool:
        settings = get_settings()
        return bool(settings.jira_base_url and settings.jira_email and settings.jira_api_token and settings.jira_project_key)

    async def request(self, method: str, path: str, **kwargs: Any) -> dict[str, Any]:
        if not self.configured:
            raise JiraError("Jira is not configured")
        try:
            async with httpx.AsyncClient(base_url=self.base_url, auth=self.auth, timeout=self.timeout) as client:
                response = await client.request(method, path, **kwargs)
                response.raise_for_status()
                return response.json() if response.content else {}
        except httpx.HTTPError as exc:
            raise JiraError("Jira request failed") from exc

    async def create_issue(self, *, summary: str, description: str, issue_type: str = "Task") -> dict[str, Any]:
        return await self.request(
            "POST",
            "/rest/api/3/issue",
            json={
                "fields": {
                    "project": {"key": self.project_key},
                    "summary": summary,
                    "description": {"type": "doc", "version": 1, "content": [{"type": "paragraph", "content": [{"type": "text", "text": description}]}]},
                    "issuetype": {"name": issue_type},
                }
            },
        )

    async def get_issue(self, issue_key: str) -> dict[str, Any]:
        return await self.request("GET", f"/rest/api/3/issue/{issue_key}")

    async def update_issue(self, issue_key: str, fields: dict[str, Any]) -> dict[str, Any]:
        return await self.request("PUT", f"/rest/api/3/issue/{issue_key}", json={"fields": fields})

    async def add_comment(self, issue_key: str, body: str) -> dict[str, Any]:
        return await self.request(
            "POST",
            f"/rest/api/3/issue/{issue_key}/comment",
            json={"body": {"type": "doc", "version": 1, "content": [{"type": "paragraph", "content": [{"type": "text", "text": body}]}]}},
        )

    async def transition_issue(self, issue_key: str, transition_id: str) -> dict[str, Any]:
        return await self.request("POST", f"/rest/api/3/issue/{issue_key}/transitions", json={"transition": {"id": transition_id}})

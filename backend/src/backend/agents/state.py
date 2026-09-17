import uuid
from typing import TypedDict

from pydantic import BaseModel, Field

from backend.schemas.document import RetrievedChunk


class AgentWorkflowState(TypedDict, total=False):
    ticket_id: uuid.UUID
    user_id: uuid.UUID | None
    original_request: str
    issue_category: str | None
    priority: str | None
    diagnosis: str | None
    retrieved_context: str | None
    retrieved_documents: list[dict]
    security_analysis: str | None
    security_risk: str | None
    resolution_plan: str | None
    resolution_result: str | None
    review_result: str | None
    requires_human_approval: bool
    workflow_id: str
    agent_run_ids: list[str]
    errors: list[str]
    messages: list[str]
    retries: int


class SupervisorOutput(BaseModel):
    issue_category: str = "general"
    priority: str = "medium"


class DiagnosisOutput(BaseModel):
    diagnosis: str


class SecurityOutput(BaseModel):
    security_analysis: str
    security_risk: str = Field(pattern="^(low|medium|high|critical)$")
    requires_human_approval: bool = False


class ResolutionOutput(BaseModel):
    resolution_plan: str
    resolution_result: str = "pending"


class ReviewerOutput(BaseModel):
    review_result: str = Field(pattern="^(approved|rejected|request_more_information)$")


def chunks_to_context(chunks: list[RetrievedChunk]) -> str:
    return "\n\n".join(f"[{chunk.title} #{chunk.chunk_index}] {chunk.content}" for chunk in chunks)

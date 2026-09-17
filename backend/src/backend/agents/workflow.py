import logging
import os
import uuid

from langgraph.graph import END, START, StateGraph
from sqlalchemy.ext.asyncio import AsyncSession

from backend.agents.nodes import (
    make_diagnosis,
    make_rag,
    make_resolution,
    make_reviewer,
    make_security,
    make_supervisor,
    make_ticket,
)
from backend.agents.state import AgentWorkflowState
from backend.core.config import get_settings
from backend.db.models.ticket import Ticket

logger = logging.getLogger(__name__)


def configure_langsmith(workflow_id: str, ticket_id: uuid.UUID) -> None:
    settings = get_settings()
    if not settings.langsmith_tracing or not settings.langsmith_api_key:
        return
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGSMITH_TRACING"] = "true"
    os.environ["LANGSMITH_API_KEY"] = settings.langsmith_api_key
    if settings.langsmith_project:
        os.environ["LANGCHAIN_PROJECT"] = settings.langsmith_project
        os.environ["LANGSMITH_PROJECT"] = settings.langsmith_project
    os.environ["LANGCHAIN_METADATA"] = f'{{"workflow_id":"{workflow_id}","ticket_id":"{ticket_id}"}}'


def should_continue(state: AgentWorkflowState) -> str:
    if len(state.get("errors", [])) >= 2:
        return "ticket"
    return "diagnosis"


def after_reviewer(state: AgentWorkflowState) -> str:
    if state.get("review_result") == "approved":
        return "ticket"
    if state.get("requires_human_approval"):
        return "ticket"
    if state.get("retries", 0) >= 1:
        return "ticket"
    return "diagnosis"


def build_workflow(session: AsyncSession):
    graph = StateGraph(AgentWorkflowState)
    graph.add_node("supervisor", make_supervisor(session))
    graph.add_node("diagnosis", make_diagnosis(session))
    graph.add_node("rag", make_rag(session))
    graph.add_node("security", make_security(session))
    graph.add_node("resolution", make_resolution(session))
    graph.add_node("reviewer", make_reviewer(session))
    graph.add_node("ticket", make_ticket(session))
    graph.add_edge(START, "supervisor")
    graph.add_conditional_edges("supervisor", should_continue, {"diagnosis": "diagnosis", "ticket": "ticket"})
    graph.add_edge("diagnosis", "rag")
    graph.add_edge("rag", "security")
    graph.add_edge("security", "resolution")
    graph.add_edge("resolution", "reviewer")
    graph.add_conditional_edges("reviewer", after_reviewer, {"diagnosis": "diagnosis", "ticket": "ticket"})
    graph.add_edge("ticket", END)
    return graph.compile()


async def run_ticket_workflow(session: AsyncSession, ticket: Ticket, user_id: uuid.UUID | None = None) -> AgentWorkflowState:
    workflow_id = str(uuid.uuid4())
    configure_langsmith(workflow_id, ticket.id)
    logger.info("workflow_start workflow_id=%s ticket_id=%s", workflow_id, ticket.id)
    state: AgentWorkflowState = {
        "ticket_id": ticket.id,
        "user_id": user_id,
        "original_request": f"{ticket.title}\n\n{ticket.description}",
        "issue_category": ticket.category,
        "priority": ticket.priority,
        "workflow_id": workflow_id,
        "agent_run_ids": [],
        "errors": [],
        "messages": [],
        "retries": 0,
        "requires_human_approval": False,
    }
    result = await build_workflow(session).ainvoke(state, {"recursion_limit": 16})
    logger.info("workflow_complete workflow_id=%s ticket_id=%s approval=%s errors=%s", workflow_id, ticket.id, result.get("requires_human_approval"), len(result.get("errors", [])))
    return result

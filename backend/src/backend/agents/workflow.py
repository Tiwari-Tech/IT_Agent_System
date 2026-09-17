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
from backend.db.models.ticket import Ticket


def should_continue(state: AgentWorkflowState) -> str:
    if len(state.get("errors", [])) >= 2:
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
    graph.add_edge("reviewer", "ticket")
    graph.add_edge("ticket", END)
    return graph.compile()


async def run_ticket_workflow(session: AsyncSession, ticket: Ticket, user_id: uuid.UUID | None = None) -> AgentWorkflowState:
    state: AgentWorkflowState = {
        "ticket_id": ticket.id,
        "user_id": user_id,
        "original_request": f"{ticket.title}\n\n{ticket.description}",
        "issue_category": ticket.category,
        "priority": ticket.priority,
        "workflow_id": str(uuid.uuid4()),
        "agent_run_ids": [],
        "errors": [],
        "messages": [],
        "retries": 0,
        "requires_human_approval": False,
    }
    return await build_workflow(session).ainvoke(state, {"recursion_limit": 16})

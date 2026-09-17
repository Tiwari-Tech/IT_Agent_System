from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.agents.prompts import load_prompt
from backend.agents.state import (
    AgentWorkflowState,
    DiagnosisOutput,
    ResolutionOutput,
    ReviewerOutput,
    SecurityOutput,
    SupervisorOutput,
    chunks_to_context,
)
from backend.agents.tracking import finish_run, start_run
from backend.ai.llm import generate_structured
from backend.rag.service import retrieve


async def tracked_node(session: AsyncSession, state: AgentWorkflowState, agent_name: str, func):
    run = await start_run(
        session,
        ticket_id=state["ticket_id"],
        workflow_id=state["workflow_id"],
        agent_name=agent_name,
        input_summary=state.get("original_request", ""),
    )
    state.setdefault("agent_run_ids", []).append(str(run.id))
    try:
        updates = await func(state)
        await finish_run(session, run, output_summary=str(updates))
        return updates
    except (RuntimeError, ValueError, SQLAlchemyError) as exc:
        errors = state.setdefault("errors", [])
        errors.append(f"{agent_name}: {exc.__class__.__name__}")
        await finish_run(session, run, error=exc.__class__.__name__)
        return {"errors": errors}


def make_supervisor(session: AsyncSession):
    async def node(state: AgentWorkflowState):
        async def work(state: AgentWorkflowState):
            prompt = f"{load_prompt('supervisor')}\nRequest: {state['original_request']}"
            result = await generate_structured(prompt, SupervisorOutput)
            return {"issue_category": result.issue_category, "priority": result.priority}

        return await tracked_node(session, state, "Supervisor", work)

    return node


def make_diagnosis(session: AsyncSession):
    async def node(state: AgentWorkflowState):
        async def work(state: AgentWorkflowState):
            prompt = f"{load_prompt('diagnosis')}\nRequest: {state['original_request']}"
            result = await generate_structured(prompt, DiagnosisOutput)
            return {"diagnosis": result.diagnosis}

        return await tracked_node(session, state, "Diagnosis", work)

    return node


def make_rag(session: AsyncSession):
    async def node(state: AgentWorkflowState):
        async def work(state: AgentWorkflowState):
            chunks = await retrieve(session, state.get("diagnosis") or state["original_request"])
            return {"retrieved_context": chunks_to_context(chunks), "retrieved_documents": [chunk.model_dump(mode="json") for chunk in chunks]}

        return await tracked_node(session, state, "RAG", work)

    return node


def make_security(session: AsyncSession):
    async def node(state: AgentWorkflowState):
        async def work(state: AgentWorkflowState):
            prompt = f"{load_prompt('security')}\nRequest: {state['original_request']}\nDiagnosis: {state.get('diagnosis')}\nContext: {state.get('retrieved_context')}"
            result = await generate_structured(prompt, SecurityOutput)
            return {
                "security_analysis": result.security_analysis,
                "security_risk": result.security_risk,
                "requires_human_approval": result.requires_human_approval or result.security_risk in {"high", "critical"},
            }

        return await tracked_node(session, state, "Security", work)

    return node


def make_resolution(session: AsyncSession):
    async def node(state: AgentWorkflowState):
        async def work(state: AgentWorkflowState):
            if state.get("requires_human_approval"):
                return {"resolution_plan": "Waiting for human approval before resolution.", "resolution_result": "waiting_for_approval"}
            prompt = f"{load_prompt('resolution')}\nDiagnosis: {state.get('diagnosis')}\nContext: {state.get('retrieved_context')}"
            result = await generate_structured(prompt, ResolutionOutput)
            return {"resolution_plan": result.resolution_plan, "resolution_result": result.resolution_result}

        return await tracked_node(session, state, "Resolution", work)

    return node


def make_reviewer(session: AsyncSession):
    async def node(state: AgentWorkflowState):
        async def work(state: AgentWorkflowState):
            prompt = f"{load_prompt('reviewer')}\nDiagnosis: {state.get('diagnosis')}\nResolution: {state.get('resolution_plan')}"
            result = await generate_structured(prompt, ReviewerOutput)
            return {"review_result": result.review_result}

        return await tracked_node(session, state, "Reviewer", work)

    return node


def make_ticket(session: AsyncSession):
    async def node(state: AgentWorkflowState):
        async def work(state: AgentWorkflowState):
            return {"messages": state.get("messages", []) + [f"Workflow {state['workflow_id']} completed with review={state.get('review_result')}"]}

        return await tracked_node(session, state, "Ticket", work)

    return node

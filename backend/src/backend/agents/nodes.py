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
from backend.db.models.ticket import Ticket
from backend.integrations.jira.service import create_or_sync_issue
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
            prompt = (
                f"{load_prompt('security')}\n"
                "Return only structured data. Do not include chain-of-thought.\n"
                f"Request: {state['original_request']}\n"
                f"Diagnosis: {state.get('diagnosis')}\n"
                f"Evidence: {state.get('retrieved_context')}\n"
                f"Current proposed resolution: {state.get('resolution_plan')}"
            )
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
                return {
                    "proposed_action": "Wait for human approval.",
                    "resolution_steps": ["Do not execute remediation until approved."],
                    "expected_result": "Approval captured before action.",
                    "rollback_plan": "No change performed.",
                    "resolution_plan": "Waiting for human approval before resolution.",
                    "resolution_result": "waiting_for_approval",
                }
            prompt = (
                f"{load_prompt('resolution')}\n"
                "Do not propose arbitrary shell or remote command execution. Return only structured data and no chain-of-thought.\n"
                f"Diagnosis: {state.get('diagnosis')}\n"
                f"Evidence: {state.get('retrieved_context')}\n"
                f"Security: {state.get('security_analysis')}\nRisk: {state.get('security_risk')}"
            )
            result = await generate_structured(prompt, ResolutionOutput)
            plan = result.resolution_plan or "\n".join(result.steps)
            return {
                "proposed_action": result.proposed_action,
                "resolution_steps": result.steps,
                "expected_result": result.expected_result,
                "rollback_plan": result.rollback_plan,
                "security_risk": result.risk,
                "requires_human_approval": result.approval_required or result.risk in {"high", "critical"},
                "resolution_plan": plan,
                "resolution_result": result.resolution_result,
            }

        return await tracked_node(session, state, "Resolution", work)

    return node


def make_reviewer(session: AsyncSession):
    async def node(state: AgentWorkflowState):
        async def work(state: AgentWorkflowState):
            prompt = (
                f"{load_prompt('reviewer')}\n"
                "Validate diagnosis, evidence, security result, and resolution. Return only structured data; no chain-of-thought.\n"
                f"Diagnosis: {state.get('diagnosis')}\n"
                f"Evidence: {state.get('retrieved_context')}\n"
                f"Security: {state.get('security_analysis')} risk={state.get('security_risk')}\n"
                f"Resolution: {state.get('resolution_plan')}\n"
                f"Rollback: {state.get('rollback_plan')}"
            )
            result = await generate_structured(prompt, ReviewerOutput)
            updates: AgentWorkflowState = {"review_result": result.review_result}
            if result.review_result != "approved":
                updates["retries"] = state.get("retries", 0) + 1
                updates["messages"] = state.get("messages", []) + [f"Reviewer: {result.feedback}"]
            return updates

        return await tracked_node(session, state, "Reviewer", work)

    return node


def make_ticket(session: AsyncSession):
    async def node(state: AgentWorkflowState):
        async def work(state: AgentWorkflowState):
            ticket = await session.get(Ticket, state["ticket_id"])
            if ticket is not None:
                comment = (
                    f"Workflow {state['workflow_id']} completed.\n"
                    f"Review: {state.get('review_result')}\n"
                    f"Risk: {state.get('security_risk')}\n"
                    f"Approval required: {state.get('requires_human_approval')}\n"
                    f"Resolution: {state.get('resolution_plan')}"
                )
                issue_key = await create_or_sync_issue(session, ticket, comment)
                if issue_key:
                    state["messages"] = state.get("messages", []) + [f"Jira issue synced: {issue_key}"]
            return {"messages": state.get("messages", []) + [f"Workflow {state['workflow_id']} completed with review={state.get('review_result')}"]}

        return await tracked_node(session, state, "Ticket", work)

    return node

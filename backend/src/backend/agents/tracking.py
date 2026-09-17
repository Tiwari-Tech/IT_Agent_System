import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models.agent_run import AgentRun
from backend.db.models.user import utc_now


async def start_run(session: AsyncSession, *, ticket_id: uuid.UUID, workflow_id: str, agent_name: str, input_summary: str) -> AgentRun:
    run = AgentRun(
        ticket_id=ticket_id,
        workflow_id=workflow_id,
        agent_name=agent_name,
        status="running",
        input_summary=input_summary[:2000],
        started_at=utc_now(),
    )
    session.add(run)
    await session.commit()
    await session.refresh(run)
    return run


async def finish_run(session: AsyncSession, run: AgentRun, *, output_summary: str = "", error: str | None = None, status: str | None = None) -> None:
    run.status = status or ("failed" if error else "completed")
    run.output_summary = output_summary[:2000] if output_summary else None
    run.error_message = error[:2000] if error else None
    run.completed_at = utc_now()
    await session.commit()

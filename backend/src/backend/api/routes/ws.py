import uuid

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from backend.core.security import decode_access_token
from backend.db.database import session_scope
from backend.db.models.user import User
from backend.services.workflows import run_workflow_for_ticket

router = APIRouter(tags=["websocket"])


async def websocket_user(websocket: WebSocket) -> User | None:
    token = websocket.query_params.get("token")
    if not token:
        return None
    try:
        user_id = uuid.UUID(str(decode_access_token(token).get("sub")))
    except (TypeError, ValueError):
        return None
    async with session_scope() as session:
        return await session.get(User, user_id)


@router.websocket("/api/v1/ws/chat")
async def chat(websocket: WebSocket) -> None:
    await websocket.accept()
    user = await websocket_user(websocket)
    if user is None or not user.is_active:
        await websocket.send_json({"type": "error", "message": "Authentication required"})
        await websocket.close(code=1008)
        return

    await websocket.send_json({"type": "connected", "user_id": str(user.id)})
    try:
        while True:
            payload = await websocket.receive_json()
            await websocket.send_json({"type": "message_received"})
            ticket_id = payload.get("ticket_id")
            if not ticket_id:
                await websocket.send_json({"type": "error", "message": "ticket_id is required"})
                continue
            try:
                ticket_uuid = uuid.UUID(str(ticket_id))
            except ValueError:
                await websocket.send_json({"type": "error", "message": "Invalid ticket_id"})
                continue

            await websocket.send_json({"type": "agent_started", "agent": "workflow"})
            async with session_scope() as session:
                db_user = await session.get(User, user.id)
                if db_user is None:
                    await websocket.send_json({"type": "error", "message": "User not found"})
                    continue
                result = await run_workflow_for_ticket(session, ticket_uuid, db_user)

            await websocket.send_json({"type": "agent_completed", "agent": "workflow", "workflow_id": result.workflow_id})
            if result.requires_human_approval:
                await websocket.send_json({"type": "approval_required", "workflow_id": result.workflow_id, "risk": result.state.get("security_risk")})
            await websocket.send_json({"type": "final_response", "result": result.model_dump(mode="json")})
    except WebSocketDisconnect:
        return
    except (RuntimeError, ValueError) as exc:
        await websocket.send_json({"type": "error", "message": exc.__class__.__name__})

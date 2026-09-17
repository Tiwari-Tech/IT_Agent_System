import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.dependencies.auth import get_current_user
from backend.db.database import get_session
from backend.db.models.user import User
from backend.schemas.user import UserSafe
from backend.services.users import get_visible_user

router = APIRouter(prefix="/api/v1/users", tags=["users"])


@router.get("/me", response_model=UserSafe)
async def me(current_user: User = Depends(get_current_user)) -> User:
    return current_user


@router.get("/{user_id}", response_model=UserSafe)
async def get_user(user_id: uuid.UUID, current_user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)) -> User:
    return await get_visible_user(session, current_user, user_id)

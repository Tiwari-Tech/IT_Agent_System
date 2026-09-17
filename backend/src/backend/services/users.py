import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models.user import User
from backend.repositories.users import get_user


async def get_visible_user(session: AsyncSession, current_user: User, user_id: uuid.UUID) -> User:
    if current_user.id != user_id and current_user.role != "it_admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role")
    user = await get_user(session, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

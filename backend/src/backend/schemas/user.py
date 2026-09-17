import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class UserSafe(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    name: str
    role: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

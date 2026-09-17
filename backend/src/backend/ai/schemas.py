from pydantic import BaseModel


class AITextRequest(BaseModel):
    prompt: str
    temperature: float | None = None


class AITextResponse(BaseModel):
    text: str

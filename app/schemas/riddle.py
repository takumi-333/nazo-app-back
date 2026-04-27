from uuid import UUID
from pydantic import BaseModel


class RandomRiddleResponse(BaseModel):
    riddle_id: UUID
    image_url: str
    has_hint: bool

    model_config = {"from_attributes": True}
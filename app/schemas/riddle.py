from uuid import UUID
from pydantic import BaseModel, Field, field_validator

# ---- GET /riddles/random ----
class RandomRiddleResponse(BaseModel):
    riddle_id: UUID
    image_url: str
    has_hint: bool

    model_config = {"from_attributes": True}


# ---- POST /riddles ----
class RiddleCreateForm(BaseModel):
    answers: list[str] = Field(..., min_length=1)
    explanation: str | None = Field(None, max_length=1000)
    hint: str | None = Field(None, max_length=500)

    @field_validator("answers")
    @classmethod
    def answers_not_empty(cls, v: list[str]) -> list[str]:
        cleaned = [a.strip() for a in v if a.strip()]
        if not cleaned:
            raise ValueError("answers には空でない文字列が最低1件必要です")
        return cleaned


class RiddleCreateResponse(BaseModel):
    id: UUID
    status: str
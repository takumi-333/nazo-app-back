from uuid import UUID

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.core.config import settings
from app.core.deps import create_access_token

router = APIRouter(prefix="/dev", tags=["dev"])


class DevTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


@router.post(
    "/token",
    response_model=DevTokenResponse,
    summary="開発用トークン発行（本番では無効）",
)
def issue_dev_token(user_id: UUID, role: str = "creator") -> DevTokenResponse:
    if not settings.DEV_MODE:
        raise HTTPException(status_code=404, detail="Not Found")

    token = create_access_token(user_id=user_id, role=role)
    return DevTokenResponse(access_token=token)
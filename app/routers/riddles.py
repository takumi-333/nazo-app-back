from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.riddle import Riddle
from app.schemas.riddle import RandomRiddleResponse

router = APIRouter(prefix="/riddles", tags=["riddles"])

@router.get(
    "/random",
    response_model=RandomRiddleResponse,
    responses={
        404: {"description": "公開済みの謎が存在しない"},
        500: {"description": "Internal Server Error"},
    },
)
def get_random_riddle(db: Session = Depends(get_db)) -> RandomRiddleResponse:
    try:
        riddle = (
            db.query(Riddle)
            .filter(Riddle.status == "published")
            .order_by(func.random())
            .limit(1)
            .one_or_none()
        )

        if riddle is None:
            raise HTTPException(status_code=404, detail="No riddles available")

        return RandomRiddleResponse(
            riddle_id=riddle.id,
            image_url=riddle.image_url,
            has_hint=riddle.has_hint
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
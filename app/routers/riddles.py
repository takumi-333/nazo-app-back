import json

from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.models.answer import Answer
from app.models.hint import Hint
from app.models.riddle import Riddle
from app.schemas.riddle import RandomRiddleResponse, RiddleCreateForm, RiddleCreateResponse, AnswerCheckRequest, AnswerCheckResponse
from app.services.image_service import process_image
from app.services.storage_service import upload_webp, get_presigned_url

router = APIRouter(prefix="/riddles", tags=["riddles"])

_ALLOWED_MIME = {"image/jpeg", "image/png", "image/gif", "image/webp"}
_MAX_IMAGE_BYTES = 5 * 1024 * 1024  # 5MB


# ---- GET /riddles/random ------------------------------------------------

@router.get(
    "/random",
    response_model=RandomRiddleResponse,
    responses={
        404: {"description": "公開済みの謎が存在しない"},
    },
    summary="公開されている謎をランダムに1件取得する"
)
async def get_random_riddle(db: AsyncSession = Depends(get_db)) -> RandomRiddleResponse:
    result = await db.execute(
        select(Riddle)
        .where(Riddle.status == "published")
        .order_by(func.random())
        .limit(1)
    )
    riddle = result.scalar_one_or_none()

    if riddle is None:
        raise HTTPException(status_code=404, detail="No riddles available")

    return RandomRiddleResponse(
        riddle_id=riddle.id,
        image_url=get_presigned_url(riddle.image_key),
        has_hint=riddle.has_hint,
    )


# ---- POST /riddles -------------------------------------------------------

@router.post(
    "",
    response_model=RiddleCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="謎を新規投稿する",
)
async def create_riddle(
    image: UploadFile,
    answers_json: str = Form(alias="answers"),
    explanation: str | None = Form(default=None),
    hint: str | None = Form(default=None),
    db: AsyncSession = Depends(get_db),
    creator_id=Depends(get_current_user_id),
) -> RiddleCreateResponse:

    # --- バリデーション ---
    if image.content_type not in _ALLOWED_MIME:
        raise HTTPException(status_code=400, detail=f"対応していない画像形式です: {image.content_type}")

    raw_bytes = await image.read()
    if len(raw_bytes) > _MAX_IMAGE_BYTES:
        raise HTTPException(status_code=413, detail="画像サイズは5MB以内にしてください")

    try:
        answers_list: list[str] = json.loads(answers_json)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="answers はJSON配列形式で送信してください")

    try:
        form = RiddleCreateForm(
            answers=answers_list,
            explanation=explanation,
            hint=hint,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # --- 画像処理 ---
    try:
        webp_bytes = process_image(raw_bytes)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"画像の処理に失敗しました: {e}")

    # --- R2アップロード ---
    try:
        image_key = upload_webp(webp_bytes)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"画像のアップロードに失敗しました: {e}")

    # --- DB保存 ---
    riddle = Riddle(
        creator_id=creator_id,
        image_key=image_key,
        explanation=form.explanation,
        status="published",
        has_hint=form.hint is not None,
    )
    db.add(riddle)
    await db.flush()

    for text in form.answers:
        db.add(Answer(riddle_id=riddle.id, answer_text=text))

    if form.hint:
        db.add(Hint(riddle_id=riddle.id, content=form.hint))

    await db.commit()
    await db.refresh(riddle)

    return RiddleCreateResponse(id=riddle.id, status=riddle.status)


# ---- POST /riddles/{id}/check -------------------------------------------------------

@router.post("/{riddle_id}/check", response_model=AnswerCheckResponse)
async def check_answer(
    riddle_id: str,
    body: AnswerCheckRequest,
    db: AsyncSession = Depends(get_db),
):
    # 謎を取得
    riddle = await db.get(Riddle, riddle_id)
    if riddle is None:
        raise HTTPException(status_code=404, detail="Riddle not found")
    
    # 諦めている場合、不正解で解説送信
    if body.give_up:
        return AnswerCheckResponse(
            correct=False,
            explanation=riddle.explanation,
        )

    # answer_text の空チェック
    if not body.answer_text or not body.answer_text.strip():
        raise HTTPException(status_code=400, detail="answer_text is required")
 
    # answers テーブルで正解候補と照合（前後空白を正規化）
    normalized_input = body.answer_text.strip()
 
    result = await db.execute(
        select(Answer).where(Answer.riddle_id == riddle_id)
    )

    answers = result.scalars().all()
 
    correct = any(
        a.answer_text.strip() == normalized_input
        for a in answers
    )
 
    return AnswerCheckResponse(
        correct=correct,
        explanation=riddle.explanation,
    )
 
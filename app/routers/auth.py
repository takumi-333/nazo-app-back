from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.core.database import get_db
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user_id,
)
from app.models.user import User
from app.schemas.user import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    MessageResponse,
    UserPublic,
)

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(body: RegisterRequest, db: AsyncSession = Depends(get_db)):
    new_user = User(
        username=body.username,
        password_hash=hash_password(body.password),
        email=body.email,
    )
    db.add(new_user)
    try:
        # ここでnew_user.idが確定
        await db.flush()
        await db.refresh(new_user)

        token = create_access_token(new_user.id, new_user.role)
        
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="そのユーザー名はすでに使用されています",
        )
    except Exception:
        await db.rollback()
        raise

    return TokenResponse(
        access_token=token,
        user=UserPublic.model_validate(new_user),
    )


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.username == body.username))
    user = result.scalar_one_or_none()

    # ユーザーが存在しない場合もパスワード照合と同じエラーを返す（列挙攻撃防止）
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="ユーザー名またはパスワードが正しくありません",
        )

    token = create_access_token(user.id, user.role)
    return TokenResponse(
        access_token=token,
        user=UserPublic.model_validate(user),
    )


@router.post("/logout", response_model=MessageResponse)
async def logout(
    _current_user_id=Depends(get_current_user_id),
):
    return MessageResponse(success=True, message="ログアウトしました")


@router.delete("/account", response_model=MessageResponse)
async def delete_account(
    current_user_id=Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await db.get(User, current_user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ユーザーが見つかりません")

    # riddles.creator_id は ON DELETE SET NULL なので物理削除するだけでよい
    await db.delete(user)
    await db.commit()
    return MessageResponse(success=True, message="アカウントを削除しました")
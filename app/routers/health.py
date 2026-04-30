from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from app.core.storage import get_storage_client
from app.core.database import Base, engine, get_db
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.core.config import settings

router = APIRouter(prefix="/health", tags=["health"])


class HealthResponse(BaseModel):
    status: str
    detail: str | None = None

@router.get("/db")
async def check_db(db: Session = Depends(get_db)):
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "ok", "db": "connected"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}


@router.get("/minio", response_model=HealthResponse)
def minio_health() -> HealthResponse:
    """MinIOへの疎通確認。バケット一覧が取得できれば正常。"""
    try:
        client = get_storage_client()
        buckets = client.list_buckets().get("Buckets", [])
        names = [b["Name"] for b in buckets]

        # 対象バケットが存在しなければ自動作成
        if settings.MINIO_BUCKET_NAME not in names:
            client.create_bucket(Bucket=settings.MINIO_BUCKET_NAME)
            return HealthResponse(
                status="ok",
                detail=f"bucket '{settings.MINIO_BUCKET_NAME}' を新規作成しました",
            )

        return HealthResponse(status="ok")

    except Exception as e:
        raise HTTPException(status_code=503, detail=f"MinIOに接続できません: {e}")
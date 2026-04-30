import uuid
from app.core.storage import get_storage_client
from app.core.config import settings

def upload_webp(data: bytes, prefix: str = "riddles") -> str:
    key = f"{prefix}/{uuid.uuid4()}.webp"
    client = get_storage_client()
    client.put_object(
        Bucket=settings.MINIO_BUCKET_NAME,
        Key=key,
        Body=data,
        ContentType="image/webp",
    )
    base = settings.MINIO_ENDPOINT_URL.rstrip("/")
    return f"{base}/{settings.MINIO_BUCKET_NAME}/{key}"
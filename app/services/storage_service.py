import uuid
from app.core.storage import get_storage_client, get_public_storage_client
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
    return key

def get_presigned_url(object_key: str, expires_in: int = 3600) -> str:
    client = get_public_storage_client()
    return client.generate_presigned_url(
        "get_object",
        Params={"Bucket": settings.MINIO_BUCKET_NAME, "Key": object_key},
        ExpiresIn=expires_in,
    )
from minio import Minio
from io import BytesIO
from app.core.config import settings

minio_client = Minio(
    settings.S3_ENDPOINT.replace("http://", ""),
    access_key=settings.AWS_ACCESS_KEY_ID,
    secret_key=settings.AWS_SECRET_ACCESS_KEY,
    secure=False
)

async def upload_to_s3(content: bytes, s3_key: str):
    try:
        minio_client.put_object(
            settings.S3_BUCKET_NAME,
            s3_key,
            data=BytesIO(content),
            length=len(content)
        )
    except Exception as e:
        raise ValueError(f"S3 upload error: {str(e)}")

def read_from_s3(s3_key: str) -> bytes:
    try:
        response = minio_client.get_object(
            settings.S3_BUCKET_NAME,
            s3_key
        )
        return response.read()
    except Exception as e:
        raise ValueError(f"S3 read error: {str(e)}")

def delete_from_s3(s3_key: str):
    try:
        minio_client.remove_object(
            settings.S3_BUCKET_NAME,
            s3_key
        )
    except Exception as e:
        raise ValueError(f"S3 delete error: {str(e)}")
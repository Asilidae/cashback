# from pydantic_settings import BaseSettings
# 
# class Settings(BaseSettings):
#     # MinIO (S3)
#     S3_ENDPOINT: str = "http://localhost:9000"
#     AWS_ACCESS_KEY_ID: str = "minioadmin"
#     AWS_SECRET_ACCESS_KEY: str = "minioadmin"
#     S3_BUCKET_NAME: str = "cashback-bucket"
# 
#     # Celery
#     CELERY_BROKER_URL: str = "redis://localhost:6379/0"
#     CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"
# 
#     # Redis
#     REDIS_URL: str = "redis://localhost:6379/2"
# 
# settings = Settings()


from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # MinIO (S3)
    S3_ENDPOINT: str = "http://172.19.79.217:9000"
    AWS_ACCESS_KEY_ID: str = "minioadmin"
    AWS_SECRET_ACCESS_KEY: str = "minioadmin"
    S3_BUCKET_NAME: str = "cashback-bucket"

    # Celery
    CELERY_BROKER_URL: str = "redis://redis:6379/0"  # Используй имя контейнера Redis
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/1"  # Используй имя контейнера Redis

    # Redis
    REDIS_URL: str = "redis://redis:6379/2"  # Используй имя контейнера Redis

settings = Settings()

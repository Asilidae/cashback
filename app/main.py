import json

from fastapi import FastAPI, File, UploadFile, HTTPException
from app.tasks.file_processing import process_file_task
from app.utils.file_utils import upload_to_s3
from app.core.config import settings
import uuid
from redis import Redis

app = FastAPI()
redis_client = Redis.from_url(settings.REDIS_URL)
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(400, "Only PDF files allowed")
    # Загрузка в S3
    content = await file.read()
    s3_key = f"uploads/{uuid.uuid4()}.pdf"
    await upload_to_s3(content, s3_key)

    # Запуск задачи Celery
    task = process_file_task.delay(s3_key)

    return {
        "task_id": task.id,
        "status_url": f"/tasks/{task.id}/status"
    }


@app.get("/tasks/{task_id}/status")
async def get_status(task_id: str):
    task = process_file_task.AsyncResult(task_id)

    if task.status == "SUCCESS":
        # Проверяем структуру результата
        result_data = task.result
        if not isinstance(result_data, dict) or "fileKey" not in result_data:
            return {"status": "error", "message": "Invalid task result format"}

        # Достаем данные из Redis
        redis_data = redis_client.get(f"cashback:{result_data['fileKey']}")
        if not redis_data:
            return {"status": "data_expired"}

        # Возвращаем результат
        return {"status": "completed", **json.loads(redis_data)}

    return {"status": task.status}
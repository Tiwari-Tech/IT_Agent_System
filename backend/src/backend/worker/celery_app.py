from celery import Celery

from backend.core.config import get_settings

settings = get_settings()
celery_app = Celery(
    "backend",
    broker=settings.celery_broker_url or settings.redis_url,
    backend=settings.celery_result_backend or settings.redis_url,
)
celery_app.conf.update(task_track_started=True, task_serializer="json", result_serializer="json", accept_content=["json"])
celery_app.autodiscover_tasks(["backend.worker"])

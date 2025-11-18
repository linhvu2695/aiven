from celery import Celery

from app.core.config import settings

def make_celery():
    # You can read broker URL from env variables
    background_url = f"redis://{settings.redis_username}:{settings.redis_password}@{settings.redis_host}:{settings.redis_port}/{settings.redis_background_database}"

    celery = Celery(
        "myapp",
        broker=background_url,
        backend=background_url,
        include=[
            "app.tasks.test_tasks",
            # "app.tasks.video_start",
            # "app.tasks.video_poll",
            # "app.tasks.video_post"
        ]
    )

    celery.conf.update(
        task_serializer="json",
        result_serializer="json",
        accept_content=["json"],
        timezone="UTC",
        enable_utc=True,
    )

    return celery

background_app = make_celery()

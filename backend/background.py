import asyncio
import logging
from celery import Celery
from celery.signals import worker_process_init, worker_process_shutdown

from app.core.config import settings
from app.core.cache import RedisCache
from app.core.database import MongoDB

# Global event loop - one per worker process
_worker_loop = None

def get_worker_loop():
    """Get or create the persistent event loop for this worker process"""
    global _worker_loop
    if _worker_loop is None:
        _worker_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(_worker_loop)
    return _worker_loop

def make_celery():
    # You can read broker URL from env variables
    background_url = f"redis://{settings.redis_username}:{settings.redis_password}@{settings.redis_host}:{settings.redis_port}/{settings.redis_background_database}"

    celery = Celery(
        "myapp",
        broker=background_url,
        backend=background_url,
        include=[
            "app.tasks.test_tasks",
            "app.tasks.video.video_poll",
            # "app.tasks.video_start",
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

# Worker lifecycle hooks
@worker_process_init.connect
def init_worker_loop(**kwargs):
    """Initialize event loop when worker process starts"""
    global _worker_loop
    _worker_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(_worker_loop)
    logger = logging.getLogger("celery")
    logger.info(f"Worker initialized with event loop: {id(_worker_loop)}")

@worker_process_shutdown.connect
def cleanup_worker_loop(**kwargs):
    """Clean up event loop and connections when worker process shuts down"""
    global _worker_loop
    logger = logging.getLogger("celery")
    
    if _worker_loop is not None:
        try:
            # Run cleanup coroutines
            _worker_loop.run_until_complete(_cleanup_async_clients())
            logger.info("Async clients cleaned up successfully")
        except Exception as e:
            logger.error(f"Error during async client cleanup: {e}")
        
        try:
            # Close the event loop
            _worker_loop.close()
            _worker_loop = None
            logger.info("Worker event loop closed")
        except Exception as e:
            logger.error(f"Error closing event loop: {e}")

async def _cleanup_async_clients():
    """Clean up async clients (Redis, MongoDB) before shutdown"""    
    # Close Redis connection
    try:
        await RedisCache().close()
    except Exception as e:
        logging.getLogger("celery").warning(f"Error closing Redis: {e}")
    
    # Close MongoDB connection
    try:
        await MongoDB().close()
    except Exception as e:
        logging.getLogger("celery").warning(f"Error closing MongoDB: {e}")

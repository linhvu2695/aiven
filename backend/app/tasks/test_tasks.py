"""
Simple test tasks for testing Celery worker functionality
"""
import time
from background import background_app


@background_app.task(name="test.add")
def add(x: int, y: int) -> int:
    """Simple addition task for testing"""
    return x + y


@background_app.task(name="test.slow_task")
def slow_task(duration: int = 5) -> dict:
    """
    A task that takes some time to complete.
    Useful for testing async behavior.
    """
    time.sleep(duration)
    return {
        "status": "completed",
        "duration": duration,
        "message": f"Task completed after {duration} seconds"
    }


@background_app.task(name="test.echo")
def echo(message: str) -> str:
    """Simple echo task that returns the input message"""
    return f"Echo: {message}"


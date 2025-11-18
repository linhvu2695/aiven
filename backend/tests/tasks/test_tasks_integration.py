"""
Integration tests for Celery tasks (with eager execution)
These tests simulate the queue behavior without needing a running worker
"""
import pytest
import time
from contextlib import contextmanager
from celery.result import AsyncResult
from background import background_app
from app.tasks.test_tasks import add, slow_task, echo


@contextmanager
def celery_eager_mode(enable: bool):
    """
    Context manager to temporarily set Celery eager mode.
    
    Args:
        enable: True to enable eager mode (tasks run synchronously),
                False to disable eager mode (tasks use real worker)
    """
    # Store original config
    original_always_eager = background_app.conf.task_always_eager
    original_eager_propagates = background_app.conf.task_eager_propagates
    
    # Set eager mode
    background_app.conf.task_always_eager = enable
    background_app.conf.task_eager_propagates = enable
    
    try:
        yield
    finally:
        # Restore original config
        background_app.conf.task_always_eager = original_always_eager
        background_app.conf.task_eager_propagates = original_eager_propagates


class TestTasksIntegration:
    """Test tasks through the Celery queue (eager mode - no worker needed)"""
    
    @pytest.fixture(scope="class", autouse=True)
    def enable_celery_eager_mode(self):
        """Configure Celery to run tasks synchronously for testing"""
        with celery_eager_mode(enable=True):
            yield
    
    def test_add_task_via_delay(self):
        """Test add task by queueing it with .delay()"""
        
        # Queue the task (runs immediately in eager mode)
        result = add.delay(10, 20)
        
        # Check that we get an AsyncResult
        assert isinstance(result, AsyncResult)
        
        # Check the result
        assert result.get() == 30
        assert result.successful()
    
    def test_add_task_via_apply_async(self):
        """Test add task by queueing it with .apply_async()"""
        
        # Queue the task with apply_async
        result = add.apply_async(args=[7, 8])
        
        assert result.get() == 15
        assert result.successful()
    
    def test_echo_task_via_delay(self):
        """Test echo task through the queue"""
        
        result = echo.delay("Test Message")
        
        assert result.get() == "Echo: Test Message"
        assert result.successful()
    
    def test_slow_task_via_delay(self):
        """Test slow task through the queue"""
        
        result = slow_task.delay(1)
        
        task_result = result.get()
        assert task_result["status"] == "completed"
        assert task_result["duration"] == 1
        assert result.successful()
    
    def test_task_id_is_generated(self):
        """Test that tasks get unique IDs"""
        
        result1 = add.delay(1, 2)
        result2 = add.delay(3, 4)
        
        # Each task should have a unique ID
        assert result1.id is not None
        assert result2.id is not None
        assert result1.id != result2.id
    
    def test_task_state(self):
        """Test task state tracking"""
        
        result = add.delay(5, 5)
        
        # In eager mode, task completes immediately
        assert result.state == 'SUCCESS'
        assert result.ready()
        assert not result.failed()


@pytest.mark.celery_worker
class TestTasksWithRealWorker:
    """
    Tests that require a real Celery worker running.
    These are skipped by default - run them manually when worker is running.
    
    To run these tests:
    1. Start Redis: docker-compose up -d
    2. Start worker: make worker
    3. Run: pytest tests/tasks/test_tasks_integration.py::TestTasksWithRealWorker --celery-worker
    """
    
    @pytest.fixture(scope="class", autouse=True)
    def check_celery_worker(self, request):
        """Skip this class if --celery-worker flag is not provided"""
        if not request.config.getoption("--celery-worker"):
            pytest.skip("Use --celery-worker flag to run tests with real worker")
    
    @pytest.fixture(scope="class", autouse=True)
    def disable_eager_mode(self):
        """Disable eager mode for real worker tests"""
        with celery_eager_mode(enable=False):
            yield
    
    def test_add_task_with_real_worker(self):
        """Test add task with actual worker (slower, tests real async behavior)"""
        result = add.delay(100, 200)
        
        # Wait for result (timeout after 10 seconds)
        task_result = result.get(timeout=10)
        
        assert task_result == 300
        assert result.successful()
    
    def test_slow_task_async_behavior(self):
        """Test that slow task actually runs asynchronously"""
        start = time.time()
        result = slow_task.delay(3)
        
        # Task should be queued immediately (< 1 second)
        elapsed = time.time() - start
        assert elapsed < 1.0, "Queueing should be instant"
        
        # Task should not be ready yet
        assert not result.ready()
        
        # Wait for result
        task_result = result.get(timeout=10)
        
        assert task_result["status"] == "completed"
        assert result.successful()


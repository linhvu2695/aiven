"""
Unit tests for Celery tasks (without worker)
These tests call the task function directly, not through the queue
"""
import pytest
from app.tasks.test_tasks import add, slow_task, echo


class TestTasksUnit:
    """Test task logic without queueing (fast, no worker needed)"""
    
    def test_add_task_direct_call(self):
        """Test add task by calling it directly"""
        result = add(5, 3)
        assert result == 8
    
    def test_add_task_negative_numbers(self):
        """Test add task with negative numbers"""
        result = add(-5, 3)
        assert result == -2
    
    def test_add_task_zero(self):
        """Test add task with zero"""
        result = add(0, 0)
        assert result == 0
    
    def test_echo_task_direct_call(self):
        """Test echo task by calling it directly"""
        result = echo("Hello World")
        assert result == "Echo: Hello World"
    
    def test_echo_task_empty_string(self):
        """Test echo task with empty string"""
        result = echo("")
        assert result == "Echo: "
    
    def test_slow_task_structure(self):
        """Test slow task returns correct structure"""
        result = slow_task(2)
        assert isinstance(result, dict)
        assert "status" in result
        assert "duration" in result
        assert "message" in result
        assert result["status"] == "completed"



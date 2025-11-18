"""
Pytest configuration and fixtures for the entire test suite
"""
import pytest


def pytest_addoption(parser):
    """Add custom command line options"""
    parser.addoption(
        "--celery-worker",
        action="store_true",
        default=False,
        help="Run tests that require a running Celery worker"
    )


def pytest_configure(config):
    """Register custom markers"""
    config.addinivalue_line(
        "markers", "celery_worker: marks tests that require a running Celery worker"
    )


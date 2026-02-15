from fastapi import APIRouter, HTTPException
from app.services.work.work_service import WorkService

router = APIRouter()


@router.get("/task/{task_id}")
async def get_task_detail(task_id: str, force_refresh: bool = False):
    """Get the latest detail for a task by its ID."""
    result = await WorkService().get_task_detail(task_id, force_refresh=force_refresh)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Cannot get task detail for {task_id}")
    return result


@router.get("/task/{task_id}/descendants")
async def get_descendants_tasks(task_id: str, force_refresh: bool = False):
    """Get all descendant tasks of a task by its ID (recursive tree traversal)."""
    results = await WorkService().get_descendants_tasks(task_id, force_refresh=force_refresh)
    return results

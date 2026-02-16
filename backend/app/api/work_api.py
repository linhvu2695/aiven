from fastapi import APIRouter, HTTPException
from app.services.work.work_service import WorkService
from app.classes.work import SetMonitorRequest

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


@router.get("/monitored")
async def get_monitored_tasks():
    """Get all monitored tasks with their descendants."""
    return await WorkService().get_monitored_tasks()


@router.put("/task/{task_id}/monitor")
async def set_task_monitor(task_id: str, body: SetMonitorRequest):
    """Set the monitor flag on a task."""
    success = await WorkService().set_task_monitor(task_id, body.monitor)
    if not success:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return {"ok": True}

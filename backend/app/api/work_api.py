from datetime import date, datetime, time, timezone

from fastapi import APIRouter, HTTPException, Query
from app.services.work.work_service import WorkService
from app.classes.work.work import SetMonitorRequest, SetAuthTokenRequest
from app.classes.work.type import TaskType

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


@router.put("/auth-token")
async def set_link_auth_token(body: SetAuthTokenRequest):
    """Inject the Link API auth token into Redis for direct use."""
    await WorkService().set_link_auth_token(body.token)
    return {"ok": True}


@router.get("/assignee/{assignee}/incomplete")
async def get_incomplete_tasks_for_assignee(
    assignee: str, subtypes: list[TaskType] = Query(default=[]), force_refresh: bool = False
):
    """Get all incomplete tasks assigned to a given person, optionally filtered by task subtypes."""
    results = await WorkService().get_incomplete_tasks_assigned_to(
        assignee, subtypes=subtypes, force_refresh=force_refresh
    )
    if results is None:
        return []
    return results


@router.get("/assignee/{assignee}/completed")
async def get_completed_tasks_for_assignee(
    assignee: str,
    subtypes: list[TaskType] = Query(default=[]),
    start_date: date | None = Query(default=None, description="Filter by completion date (inclusive)"),
    end_date: date | None = Query(default=None, description="Filter by completion date (inclusive)"),
    force_refresh: bool = False,
):
    """Get completed tasks assigned to a given person, optionally filtered by subtypes and completion date range."""
    tz = timezone.utc
    start_dt = datetime.combine(start_date, time.min, tzinfo=tz) if start_date else None
    end_dt = datetime.combine(end_date, time.max, tzinfo=tz) if end_date else None
    results = await WorkService().get_completed_tasks_assigned_to(
        assignee,
        subtypes=subtypes,
        start_date=start_dt,
        end_date=end_dt,
        force_refresh=force_refresh,
    )
    return results or []


@router.get("/team/workload")
async def get_team_workload(subtypes: list[TaskType] = Query(default=[]), force_refresh: bool = False):
    """Get workload summary for all team members, optionally filtered by task subtypes."""
    return await WorkService().get_team_workload(subtypes=subtypes, force_refresh=force_refresh)

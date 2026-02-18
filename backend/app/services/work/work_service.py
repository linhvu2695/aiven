import asyncio
import json
import logging
from datetime import datetime, timezone

import httpx

from app.core.database import MongoDB
from app.core.cache import RedisCache
from app.classes.work.status import COMPLETE_STATUSES
from app.classes.work.work import TaskDetail
from app.classes.work.type import TaskType
from app.classes.work.team import TEAM_MEMBERS

INCOMPLETE_TASKS_CACHE_TTL = 3600  # 1 hour

TASK_COLLECTION_NAME = "tasks"

LINK_URL = "https://link.orangelogic.com"
LINK_SEARCH_API_URL = f"{LINK_URL}/API/Search/v4.0/Search"
COUNT_PER_PAGE = 300

TASK_DETAIL_FIELDS = [
    "CoreField.Title", 
    "CoreField.Identifier",
    "CoreField.DocSubType", 
    "CoreField.Status",
    "Document.TimeSpentMn", 
    "Document.TimeLeftMn", 
    "AssignedTo",
    "dev.Main-dev-team",
    "Document.CurrentEstimatedCompletionDate", 
    "Document.CortexShareLinkRaw",
    "product.Importance-for-next-release", 
    "Document.Dependencies",
    "Document.CurrentEstimatedStartDate", 
    "Document.CurrentEstimatedEndDate",
    "ParentFolderIdentifier"
]

class WorkService:
    _instance = None
    logger = logging.getLogger("uvicorn.error")

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance") or cls._instance is None:
            cls._instance = super(WorkService, cls).__new__(cls)
        return cls._instance

    async def get_task_detail(self, task_id: str, force_refresh: bool = False) -> TaskDetail | None:
        """
        Fetch the latest detail for a task by its ID.
        Stores/updates the task in MongoDB.
        """
        db = MongoDB()

        if not force_refresh:
            # 1. Check MongoDB first
            docs = await db.find_documents_by_field(TASK_COLLECTION_NAME, "identifier", task_id)
            if docs:
                doc = docs[0]
                doc.pop("_id", None)
                return TaskDetail(**doc)

        # 2. Fetch from external API
        task_detail = await self._fetch_task_from_api(task_id)
        if task_detail is None:
            return None

        # 3. Upsert into MongoDB
        await self._upsert_task(task_detail)

        return task_detail

    async def get_descendants_tasks(self, task_id: str, force_refresh: bool = False) -> list[TaskDetail]:
        """
        Get all descendant tasks of a task by its ID, traversing the tree recursively.
        Results are stored/updated in MongoDB.
        """
        if not force_refresh:
            # Try to get from MongoDB first
            descendants = await self._get_descendants_from_db(task_id)
            if descendants:
                return descendants

        # Fetch from API recursively and upsert into MongoDB
        return await self._fetch_and_store_descendants(task_id)

    def _cache_key_incomplete_tasks_assigned_to(self, assignee: str, subtype: str) -> str:
        return f"work:incomplete:{assignee.lower()}:{subtype}"

    async def get_incomplete_tasks_assigned_to(
        self, assignee: str, subtypes: list[TaskType] = [], force_refresh: bool = False
    ) -> list[TaskDetail] | None:
        """
        Get incomplete tasks assigned to a user.
        Caches per subtype in Redis (1h TTL) to avoid redundant storage across
        subtype combinations. Merges cached results on read.
        """
        cache = RedisCache()
        types_to_fetch = list(TaskType) if not subtypes else subtypes

        if not force_refresh:
            # 1. Try to get from Redis first
            cached_lists: list[list[TaskDetail]] = []
            all_hit = True
            for t in types_to_fetch:
                key = self._cache_key_incomplete_tasks_assigned_to(assignee, t.value)
                raw = await cache.get(key)
                if raw is not None:
                    cached_lists.append([TaskDetail(**x) for x in json.loads(raw)])
                else:
                    all_hit = False
                    break

            if all_hit:
                # 1.1. Merge cached results into a single list
                seen: set[str] = set()
                merged: list[TaskDetail] = []
                for lst in cached_lists:
                    for task in lst:
                        if task.identifier not in seen:
                            seen.add(task.identifier)
                            merged.append(task)
                return merged

        # 2. Fetch from API (force refresh or cache miss)
        query = f"participant(\"Assigned to\"):(\"{assignee}\") AND NOT (WorkflowStatus:({' OR '.join(COMPLETE_STATUSES)}))"
        if subtypes:
            string_subtypes = [f"\"{s}\"" for s in subtypes]
            query += f" AND DocSubType:({' OR '.join(string_subtypes)})"

        results = await self._query_tasks_from_api(query)
        if not results:
            for t in types_to_fetch:
                await cache.set(
                    self._cache_key_incomplete_tasks_assigned_to(assignee, t.value),
                    "[]",
                    expiration=INCOMPLETE_TASKS_CACHE_TTL,
                )
            return None

        # 3. Distribute tasks to per-type caches (only for types we fetched)
        by_type: dict[str, list[TaskDetail]] = {t.value: [] for t in types_to_fetch}
        for task in results:
            type_val = (task.doc_sub_type or "other").lower().strip()
            if type_val in by_type:
                by_type[type_val].append(task)
            else:
                by_type.setdefault("other", []).append(task)

        for type_val, tasks in by_type.items():
            key = self._cache_key_incomplete_tasks_assigned_to(assignee, type_val)
            await cache.set(
                key,
                json.dumps([t.model_dump(mode="json") for t in tasks]),
                expiration=INCOMPLETE_TASKS_CACHE_TTL,
            )

        # 4. Upsert tasks into MongoDB
        for task in results:
            await self._upsert_task(task)

        return results

    async def get_team_workload(self, subtypes: list[TaskType] = [], force_refresh: bool = False) -> list[dict]:
        """
        Fetch incomplete tasks for every team member in parallel
        and return per-member workload summaries.
        """
        async def fetch_member(name: str) -> dict:
            tasks = await self.get_incomplete_tasks_assigned_to(name, subtypes=subtypes, force_refresh=force_refresh) or []
            time_spent = sum(t.time_spent_mn for t in tasks)
            time_left = sum(t.time_left_mn for t in tasks)
            return {
                "name": name,
                "task_count": len(tasks),
                "time_spent_mn": time_spent,
                "time_left_mn": time_left,
                "tasks": [t.model_dump() for t in tasks],
            }

        results = await asyncio.gather(*(fetch_member(name) for name in TEAM_MEMBERS))
        return sorted(results, key=lambda r: r["time_left_mn"], reverse=True)

    async def _get_descendants_from_db(self, task_id: str) -> list[TaskDetail]:
        """
        Recursively collect all descendants from MongoDB by traversing
        the parent_folder_identifier tree.
        """
        db = MongoDB()
        descendants: list[TaskDetail] = []

        # Find direct children
        children_docs = await db.find_documents_by_field(
            TASK_COLLECTION_NAME, "parent_folder_identifier", task_id
        )

        for doc in children_docs:
            doc.pop("_id", None)
            task = TaskDetail(**doc)
            descendants.append(task)
            # Recurse into each child's subtree
            child_descendants = await self._get_descendants_from_db(task.identifier)
            descendants.extend(child_descendants)

        return descendants

    async def _fetch_and_store_descendants(self, task_id: str) -> list[TaskDetail]:
        """
        Recursively fetch all descendants from the API and upsert each into MongoDB.
        """
        descendants: list[TaskDetail] = []

        # Fetch direct children from API
        children = await self._fetch_descendants_tasks_from_api(task_id)
        if not children:
            return descendants

        for child in children:
            await self._upsert_task(child)
            descendants.append(child)
            # Recurse into each child's subtree
            child_descendants = await self._fetch_and_store_descendants(child.identifier)
            descendants.extend(child_descendants)

        return descendants

    async def get_monitored_tasks(self) -> list[TaskDetail]:
        """
        Return all tasks where monitor=True.
        """
        db = MongoDB()
        cursor = db.database[TASK_COLLECTION_NAME].find({"monitor": True})
        results = []
        async for doc in cursor:
            doc.pop("_id", None)
            results.append(TaskDetail(**doc))
        return results

    async def set_task_monitor(self, task_id: str, monitor: bool) -> bool:
        """
        Set the monitor flag on a task in MongoDB.
        Returns True if the task was found and updated.
        """
        db = MongoDB()
        existing = await db.find_documents_by_field(TASK_COLLECTION_NAME, "identifier", task_id)
        if not existing:
            return False
        doc = existing[0]
        await db.update_document(TASK_COLLECTION_NAME, str(doc["_id"]), {"monitor": monitor})
        return True

    async def _upsert_task(self, task: TaskDetail) -> None:
        """
        Upsert a task into MongoDB by its identifier.
        """
        db = MongoDB()
        document = task.model_dump()
        document["updated_at"] = datetime.now(timezone.utc).isoformat()
        existing = await db.find_documents_by_field(TASK_COLLECTION_NAME, "identifier", task.identifier)
        if existing:
            # Preserve the existing monitor flag
            document["monitor"] = existing[0].get("monitor", False)

            await db.update_document(TASK_COLLECTION_NAME, str(existing[0]["_id"]), document)
        else:
            document["created_at"] = datetime.now(timezone.utc).isoformat()
            await db.insert_document(TASK_COLLECTION_NAME, document)

    async def _get_auth_token(self) -> str:
        """
        Retrieve the authorization token for the Link API.
        """
        return ""

    async def _query_tasks_from_api(self, query: str) -> list[TaskDetail] | None:
        """
        Call the Link Search API to query tasks.
        """
        token = await self._get_auth_token()

        params = {
            "query": f"({query}) AND DocType:Project",
            "fields": TASK_DETAIL_FIELDS,
            "format": "JSON",
            "token": token,
            "countperpage": COUNT_PER_PAGE,
        }

        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.get(LINK_SEARCH_API_URL, params=params)
                response.raise_for_status()
                data = response.json()
                items = data.get("APIResponse", {}).get("Items", [])
                return [TaskDetail.from_api_response(item) for item in items]
        except httpx.HTTPStatusError as e:
            self.logger.error(f"Link API returned {e.response.status_code} for query {query}: {e.response.text}")
            return None
        except httpx.RequestError as e:
            self.logger.error(f"Failed to reach Link API for query {query}: {e}")
            return None

    async def _fetch_task_from_api(self, task_id: str) -> TaskDetail | None:
        """
        Call the Link Search API to get the latest task detail.
        """
        results = await self._query_tasks_from_api(f"SystemIdentifier:{task_id}")
        if not results:
            return None
        return results[0] if len(results) > 0 else None

    async def _fetch_descendants_tasks_from_api(self, task_id: str) -> list[TaskDetail] | None:
        """
        Call the Link Search API to get the descendants tasks of a task.
        """
        results = await self._query_tasks_from_api(f"ParentFolderIdentifier:{task_id}")
        if not results:
            return None
        return results
import logging
from datetime import datetime, timezone

import httpx

from app.core.database import MongoDB
from app.classes.work import TaskDetail

TASK_COLLECTION_NAME = "tasks"

LINK_URL = "https://link.orangelogic.com"
LINK_SEARCH_API_URL = f"{LINK_URL}/API/Search/v4.0/Search"

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

    async def _upsert_task(self, task: TaskDetail) -> None:
        """
        Upsert a task into MongoDB by its identifier.
        """
        db = MongoDB()
        document = task.model_dump()
        document["updated_at"] = datetime.now(timezone.utc).isoformat()
        existing = await db.find_documents_by_field(TASK_COLLECTION_NAME, "identifier", task.identifier)
        if existing:
            await db.update_document(TASK_COLLECTION_NAME, str(existing[0]["_id"]), document)
        else:
            document["created_at"] = datetime.now(timezone.utc).isoformat()
            await db.insert_document(TASK_COLLECTION_NAME, document)

    async def _get_auth_token(self) -> str:
        """
        Retrieve the authorization token for the Link API.
        """
        return "Cortexmmf9RZQcbMlThtylPiHVb0AoZ5TfjJgZCo851Mf30bcFTfCsR9KK4cpdLNSwQFUU"

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
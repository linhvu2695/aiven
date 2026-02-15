import json
import logging

import httpx

from app.core.cache import RedisCache

TASK_CACHE_KEY_PREFIX = "work:task:"
TASK_CACHE_EXPIRATION = 3600  # 1 hour

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

    async def get_task_detail(self, task_id: str, force_refresh: bool = False) -> dict | None:
        """
        Fetch the latest detail for a task by its ID.
        Results are cached in Redis for 1 hour.
        """
        cache_key = f"{TASK_CACHE_KEY_PREFIX}{task_id}"

        if force_refresh:
            await RedisCache().redis.delete(cache_key)

        # 1. Check cache first
        cached = await RedisCache().get(cache_key)
        if cached:
            return json.loads(cached)

        # 2. Fetch from external API
        task_detail = await self._fetch_task_from_api(task_id)
        if task_detail is None:
            return None

        # 3. Store in cache
        await RedisCache().set(cache_key, json.dumps(task_detail), expiration=TASK_CACHE_EXPIRATION)

        return task_detail

    async def _get_auth_token(self) -> str:
        """
        Retrieve the authorization token for the Link API.
        """
        return ""

    async def _fetch_task_from_api(self, task_id: str) -> dict | None:
        """
        Call the Link Search API to get the latest task detail.
        """
        results = await self._query_tasks_from_api(f"SystemIdentifier:{task_id}")
        if not results:
            return None
        return results[0] if len(results) > 0 else None

    async def _query_tasks_from_api(self, query: str) -> list[dict] | None:
        """
        Call the Link Search API to query tasks.
        """
        token = await self._get_auth_token()

        params = {
            "query": query,
            "fields": TASK_DETAIL_FIELDS,
            "format": "JSON",
            "token": token,
        }

        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.get(LINK_SEARCH_API_URL, params=params)
                response.raise_for_status()
                data = response.json()
                return data.get("APIResponse", {}).get("Items", [])
        except httpx.HTTPStatusError as e:
            self.logger.error(f"Link API returned {e.response.status_code} for query {query}: {e.response.text}")
            return None
        except httpx.RequestError as e:
            self.logger.error(f"Failed to reach Link API for query {query}: {e}")
            return None

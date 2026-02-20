from app.core.config import settings
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
import logging
from bson import ObjectId
from typing import Dict, Any, Optional


class MongoDB:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(MongoDB, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, '_initialized') and self._initialized:
            return
        
        host = settings.mongodb_host
        port = settings.mongodb_port
        user = settings.mongodb_root_username
        password = settings.mongodb_root_password
        db_name = settings.mongodb_db_name

        mongodb_uri = f"mongodb://{user}:{password}@{host}:{port}"
        self.client = AsyncIOMotorClient(
            mongodb_uri,
            maxPoolSize=settings.mongodb_max_pool_size,
            minPoolSize=settings.mongodb_min_pool_size,
            maxIdleTimeMS=settings.mongodb_max_idle_time_ms
        )
        self.database = self.client.get_database(db_name)
        self._initialized = True

    async def close(self):
        """Close MongoDB connection"""
        if hasattr(self, 'client') and self.client:
            self.client.close()
            self._initialized = False

    async def check_health(self):
        """Check MongoDB connection health"""
        try:
            await self.database.command("ping")
            logging.getLogger("uvicorn.info").info("Successfully connected to MongoDB")
            return True
        except Exception as ex:
            logging.getLogger("uvicorn.error").error(f"Fail to connect to MongoDB: {ex}")
            return False

    async def get_document(self, collection_name: str, id: str, convert_object_id: bool = False) -> dict:
        """Get a document by ID from a collection"""
        try:
            obj_id = ObjectId(id)
        except Exception:
            raise ValueError("Invalid document id format")
        
        document = await self.database[collection_name].find_one({"_id": obj_id})

        if not document:
            raise ValueError(f"Document {id} not found in collection {collection_name}")
        
        # Convert MongoDB _id to id if needed
        if convert_object_id and "_id" in document:
            document["id"] = str(document["_id"])
            del document["_id"]

        return document

    async def insert_document(self, collection_name: str, document: dict) -> str:
        """Insert a document into a collection"""
        result = await self.database[collection_name].insert_one(document)
        return str(result.inserted_id)
        
    async def update_document(self, collection_name: str, id: str, document: dict) -> bool:
        """
        Update a document in MongoDB.
        
        Returns:
            bool: True if the document was updated or upserted, False otherwise
        """
        result = await self.database[collection_name].update_one(
            {"_id": ObjectId(id)},
            {"$set": document},
            upsert=True
        )
        # Success if either matched an existing doc OR inserted a new one (upsert)
        return result.matched_count > 0 or result.upserted_id is not None

    async def list_documents(self, collection_name: str, convert_object_id: bool = False) -> list[dict]:
        """List all documents in a collection"""
        cursor = self.database[collection_name].find()
        documents = []
        async for document in cursor:
            # Convert MongoDB _id to id if needed
            if convert_object_id and "_id" in document:
                document["id"] = str(document["_id"])
                del document["_id"]
            documents.append(document)
        return documents

    async def find_documents_by_field(self, collection_name: str, field_name: str, field_value: str) -> list[dict]:
        """Find documents where a specific field matches a given value."""
        cursor = self.database[collection_name].find({field_name: field_value})
        documents = []
        async for document in cursor:
            documents.append(document)
        return documents

    async def find_documents_with_filters(
        self,
        collection_name: str,
        filters: Dict[str, Any],
        skip: int = 0,
        limit: Optional[int] = None,
        sort_by: Optional[str] = None,
        asc: bool = True,
        collation: Optional[Dict[str, Any]] = None,
    ) -> list[dict]:
        """
        Find documents with multiple field filters and optional pagination/sorting.

        Args:
            collection_name: Name of the MongoDB collection
            filters: Dictionary of field-value pairs to filter by
            skip: Number of documents to skip (for pagination)
            limit: Maximum number of documents to return
            sort_by: Field name to sort by
            asc: True for ascending, False for descending
            collation: Optional MongoDB collation (e.g. {"locale": "en", "strength": 2} for case-insensitive)

        Returns:
            List of matching documents

        Example:
            # Find images that are plant photos, not deleted, for a specific entity
            filters = {
                "image_type": "plant_photo",
                "is_deleted": False,
                "entity_id": "plant123"
            }
            docs = await MongoDB().find_documents_with_filters("images", filters, limit=10)
        """
        find_kwargs: Dict[str, Any] = {}
        if collation is not None:
            find_kwargs["collation"] = collation
        cursor = self.database[collection_name].find(filters, **find_kwargs)
        
        # Apply sorting if specified
        if sort_by:
            cursor = cursor.sort(sort_by, 1 if asc else -1)
        
        # Apply pagination
        if skip > 0:
            cursor = cursor.skip(skip)
        if limit:
            cursor = cursor.limit(limit)
        
        documents = []
        async for document in cursor:
            documents.append(document)
        return documents

    async def count_documents_with_filters(self, collection_name: str, filters: Dict[str, Any]) -> int:
        """Count documents matching the given filters."""
        return await self.database[collection_name].count_documents(filters)

    async def delete_document(self, collection_name: str, id: str) -> bool:
        """Delete a document from a collection"""
        result = await self.database[collection_name].delete_one({"_id": ObjectId(id)})
        return result.deleted_count > 0


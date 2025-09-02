from app.core.config import settings
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
import logging
from bson import ObjectId
from typing import Dict, Any, Optional

def get_mongodb_conn() -> AsyncIOMotorDatabase:
    host = settings.mongodb_host
    port = settings.mongodb_port
    user = settings.mongodb_root_username
    password = settings.mongodb_root_password
    db_name = settings.mongodb_db_name

    mongodb_uri = f"mongodb://{user}:{password}@{host}:{port}"
    mongo_client = AsyncIOMotorClient(mongodb_uri)
    mongodb = mongo_client.get_database(db_name)
    
    return mongodb

async def check_mongodb_health():
    try:
        conn = get_mongodb_conn()
        await conn.command("ping")
        logging.getLogger("uvicorn.info").info("Successfully connected to MongoDB")
        return True
    except Exception as ex:
        logging.getLogger("uvicorn.error").error(f"Fail to connect to MongoDB: {ex}")
        return False

async def get_document(collection_name: str, id: str, convert_object_id: bool = False) -> dict:
    try:
        obj_id = ObjectId(id)
    except Exception:
        raise ValueError("Invalid document id format")
    
    db = get_mongodb_conn()
    document = await db[collection_name].find_one({"_id": obj_id})

    if not document:
        raise ValueError("Document not found")
    
    # Convert MongoDB _id to id if needed
    if convert_object_id and "_id" in document:
        document["id"] = str(document["_id"])
        del document["_id"]

    return document

async def insert_document(collection_name: str, document: dict) -> str:
    db = get_mongodb_conn()
    result = await db[collection_name].insert_one(document)
    return str(result.inserted_id)
    
async def update_document(collection_name: str, id: str, document: dict) -> str | None:
    db = get_mongodb_conn()
    result = await db[collection_name].update_one(
        {"_id": ObjectId(id)},
        {"$set": document},
        upsert=True
    )
    return result.upserted_id

async def list_documents(collection_name: str, convert_object_id: bool = False) -> list[dict]:
    db = get_mongodb_conn()
    cursor = db[collection_name].find()
    documents = []
    async for document in cursor:
        documents.append(document)

        # Convert MongoDB _id to id if needed
        if convert_object_id and "_id" in document:
            document["id"] = str(document["_id"])
            del document["_id"]
    return documents

async def find_documents_by_field(collection_name: str, field_name: str, field_value: str) -> list[dict]:
    """Find documents where a specific field matches a given value."""
    db = get_mongodb_conn()
    cursor = db[collection_name].find({field_name: field_value})
    documents = []
    async for document in cursor:
        documents.append(document)
    return documents

async def find_documents_with_filters(
    collection_name: str, 
    filters: Dict[str, Any], 
    skip: int = 0, 
    limit: Optional[int] = None,
    sort_by: Optional[str] = None,
    asc: bool = True
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
    
    Returns:
        List of matching documents
        
    Example:
        # Find images that are plant photos, not deleted, for a specific entity
        filters = {
            "image_type": "plant_photo",
            "is_deleted": False,
            "entity_id": "plant123"
        }
        docs = await find_documents_with_filters("images", filters, limit=10)
    """
    db = get_mongodb_conn()
    cursor = db[collection_name].find(filters)
    
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

async def count_documents_with_filters(collection_name: str, filters: Dict[str, Any]) -> int:
    """Count documents matching the given filters."""
    db = get_mongodb_conn()
    return await db[collection_name].count_documents(filters)

async def delete_document(collection_name: str, id: str) -> bool:
    db = get_mongodb_conn()
    result = await db[collection_name].delete_one({"_id": ObjectId(id)})
    return result.deleted_count > 0
from app.core.config import settings
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
import logging
from bson import ObjectId

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

async def get_document(collection_name: str, id: str) -> dict:
    try:
        obj_id = ObjectId(id)
    except Exception:
        raise ValueError("Invalid document id format")
    
    db = get_mongodb_conn()
    document = await db[collection_name].find_one({"_id": obj_id})

    if not document:
        raise ValueError("Document not found")
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

async def list_documents(collection_name: str) -> list[dict]:
    db = get_mongodb_conn()
    cursor = db[collection_name].find()
    documents = []
    async for document in cursor:
        documents.append(document)
    return documents

async def find_documents_by_field(collection_name: str, field_name: str, field_value: str) -> list[dict]:
    """Find documents where a specific field matches a given value."""
    db = get_mongodb_conn()
    cursor = db[collection_name].find({field_name: field_value})
    documents = []
    async for document in cursor:
        documents.append(document)
    return documents

async def delete_document(collection_name: str, id: str) -> bool:
    db = get_mongodb_conn()
    result = await db[collection_name].delete_one({"_id": ObjectId(id)})
    return result.deleted_count > 0
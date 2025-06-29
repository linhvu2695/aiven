from app.core.config import settings
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
import logging
from bson import ObjectId

def _get_mongodb_conn() -> AsyncIOMotorDatabase:
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
        conn = _get_mongodb_conn()
        await conn.command("ping")
        logging.getLogger("uvicorn.error").info("Successfully connected to MongoDB")
        return True
    except Exception as ex:
        logging.getLogger("uvicorn.error").error(f"Fail to connect to MongoDB: {ex}")
        return False

async def get_document(collection_name: str, id: str) -> dict:
    try:
        obj_id = ObjectId(id)
    except Exception:
        raise ValueError("Invalid document id format")
    
    db = _get_mongodb_conn()
    document = await db[collection_name].find_one({"_id": obj_id})

    if not document:
        raise ValueError("Document not found")
    return document

async def insert_document(collection_name: str, document: dict) -> str:
    db = _get_mongodb_conn()
    result = await db[collection_name].insert_one(document)
    return str(result.inserted_id)
    
async def update_document(collection_name: str, id: str, document: dict) -> str | None:
    db = _get_mongodb_conn()
    result = await db[collection_name].update_one(
        {"_id": ObjectId(id)},
        {"$set": document},
        upsert=True
    )
    return result.upserted_id
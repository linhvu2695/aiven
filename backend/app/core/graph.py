from neo4j import AsyncGraphDatabase
from app.core.config import settings
import logging
from typing import Optional


class Neo4j:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Neo4j, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, '_initialized') and self._initialized:
            return
        
        uri = settings.neo4j_uri
        username = settings.neo4j_username
        password = settings.neo4j_password
        database = settings.neo4j_database
        max_connection_pool_size = settings.neo4j_max_connection_pool_size

        self.driver = AsyncGraphDatabase.driver(
            uri,
            auth=(username, password),
            max_connection_pool_size=max_connection_pool_size
        )
        self.database = database
        self._initialized = True

    async def close(self):
        """Close Neo4j connection"""
        if hasattr(self, 'driver') and self.driver:
            await self.driver.close()
            self._initialized = False

    async def check_health(self):
        """Check Neo4j connection health"""
        try:
            async with self.driver.session(database=self.database) as session:
                result = await session.run("RETURN 1 as health")
                await result.consume()
            logging.getLogger("uvicorn.info").info("Successfully connected to Neo4j")
            return True
        except Exception as ex:
            logging.getLogger("uvicorn.error").error(f"Failed to connect to Neo4j: {ex}")
            return False

    def get_session(self, database: Optional[str] = None):
        """Get a Neo4j session for direct usage"""
        db = database or self.database
        return self.driver.session(database=db)


import json
from graphiti_core.embedder.openai import OpenAIEmbedder, OpenAIEmbedderConfig
from graphiti_core.llm_client import LLMConfig, OpenAIClient
from neo4j import AsyncGraphDatabase
from app.core.config import settings
import logging
from typing import Optional
from datetime import datetime
from graphiti_core import Graphiti as GraphitiCore
from graphiti_core.nodes import EpisodeType


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


class Graphiti:
    """
    Wrapper around Graphiti Core for building knowledge graphs.
    Uses Neo4j as the backend database and OpenAI for LLM inference.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Graphiti, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, '_initialized') and self._initialized:
            return
        
        uri = settings.neo4j_uri
        username = settings.neo4j_username
        password = settings.neo4j_password

        # Initialize LLM client
        openai_config = LLMConfig(api_key=settings.openai_api_key, model="gpt-4o-mini")
        openai_client = OpenAIClient(config=openai_config)
        openai_embedder_config = OpenAIEmbedderConfig(
            api_key=settings.openai_api_key, 
            embedding_model="text-embedding-3-large"
            )
        openai_embedder_client = OpenAIEmbedder(config=openai_embedder_config)
        
        # Initialize Graphiti with Neo4j connection
        self.graphiti = GraphitiCore(
            uri=uri,
            user=username,
            password=password,
            llm_client=openai_client,
            embedder=openai_embedder_client,
        )
        self._initialized = True
        self._indices_built = False

    async def build_indices_and_constraints(self):
        """
        Initialize Graphiti by building indices and constraints.
        This should be called once during application startup.
        """
        if not self._indices_built:
            try:
                await self.graphiti.build_indices_and_constraints()
                self._indices_built = True
                logging.getLogger("uvicorn.info").info("Graphiti indices and constraints built successfully")
            except Exception as ex:
                logging.getLogger("uvicorn.error").error(f"Failed to build Graphiti indices: {ex}")
                raise

    async def add_text_episode(
        self,
        name: str,
        text: str,
        description: str,
        reference_time: Optional[datetime] = None,
        **kwargs
    ):
        """
        Add a text episode to the knowledge graph.
        
        Args:
            name: Name/identifier for the episode
            text: The text content of the episode
            description: Description of the episode
            reference_time: Optional timestamp for the episode (defaults to now)
            **kwargs: Additional parameters for add_text_episode
        
        Returns:
            The created text episode results
        """
        if not self._indices_built:
            await self.build_indices_and_constraints()
        
        return await self.graphiti.add_episode(
            name=name,
            episode_body=text,
            source_description=description,
            source=EpisodeType.text,
            reference_time=reference_time or datetime.now(),
            **kwargs
        )

    async def add_json_episode(
        self,
        name: str,
        data: dict,
        description: str,
        reference_time: Optional[datetime] = None,
        **kwargs
    ):
        """
        Add a JSON episode to the knowledge graph.
        
        Args:
            name: Name/identifier for the episode
            json: The JSON content of the episode
            description: Description of the episode
            reference_time: Optional timestamp for the episode (defaults to now)
            **kwargs: Additional parameters for add_json_episode
        
        Returns:
            The created JSON episode results
        """
        if not self._indices_built:
            await self.build_indices_and_constraints()
        
        return await self.graphiti.add_episode(
            name=name,
            episode_body=json.dumps(data),
            source_description=description,
            source=EpisodeType.json,
            reference_time=reference_time or datetime.now(),
            **kwargs
        )

    async def add_message_episode(
        self,
        name: str,
        role: str,
        content: str,
        description: str,
        reference_time: Optional[datetime] = None,
        **kwargs
    ):
        """
        Add a message episode to the knowledge graph.
        
        Args:
            name: Name/identifier for the episode
            role: Role of the message (user or assistant)
            content: Content of the message
            description: Description of the episode
            reference_time: Optional timestamp for the episode (defaults to now)
            **kwargs: Additional parameters for add_message_episode
        """
        if not self._indices_built:
            await self.build_indices_and_constraints()
        
        return await self.graphiti.add_episode(
            name=name,
            episode_body=json.dumps({"role": role, "content": content}),
            source_description=description,
            source=EpisodeType.message,
            reference_time=reference_time or datetime.now(),
            **kwargs
        )

    async def search(
        self,
        query: str,
        num_results: int = 10,
        center_node_uuid: Optional[str] = None,
        group_ids: Optional[list[str]] = None
    ):
        """
        Search for entities and relationships in the knowledge graph.
        
        Args:
            query: Search query string
            num_results: Maximum number of results to return (default: 10)
            center_node_uuid: Optional UUID of a center node to search around
            group_ids: Optional list of group IDs to filter by
        
        Returns:
            List of matching EntityEdge objects
        """
        return await self.graphiti.search(
            query=query,
            num_results=num_results,
            center_node_uuid=center_node_uuid,
            group_ids=group_ids
        )

    async def retrieve_episodes(
        self,
        reference_time: Optional[datetime] = None,
        last_n: int = 3,
        group_ids: Optional[list[str]] = None,
        source: Optional[EpisodeType] = None
    ):
        """
        Retrieve episodes from the knowledge graph.
        
        Args:
            reference_time: Optional timestamp to retrieve episodes from (defaults to now)
            last_n: Number of recent episodes to retrieve (default: 3)
            group_ids: Optional list of group IDs to filter by
            source: Optional episode type to filter by
        
        Returns:
            List of episodes
        """
        ts = reference_time or datetime.now()
        return await self.graphiti.retrieve_episodes(
            reference_time=ts,
            last_n=last_n,
            group_ids=group_ids,
            source=source
        )

    async def get_nodes_and_edges_by_episode(self, episode_uuids: list[str]):
        """
        Get all nodes and edges associated with specific episodes.
        
        Args:
            episode_uuids: List of episode UUIDs
        
        Returns:
            Nodes and edges for the episodes
        """
        return await self.graphiti.get_nodes_and_edges_by_episode(episode_uuids)

    async def check_health(self):
        """Check Graphiti connection health"""
        try:
            if not self._indices_built:
                await self.build_indices_and_constraints()

            # Try a simple search to verify connection
            await self.search(query="test", num_results=1)
            logging.getLogger("uvicorn.info").info("Successfully connected to Graphiti")
            return True
        except Exception as ex:
            logging.getLogger("uvicorn.error").error(f"Failed to connect to Graphiti: {ex}")
            return False

    async def close(self):
        """Close Graphiti connection"""
        if hasattr(self, 'graphiti') and self.graphiti:
            await self.graphiti.close()
            self._initialized = False
            self._indices_built = False
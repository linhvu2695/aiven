from collections.abc import Sequence
import asyncio, logging
from datetime import datetime, timezone
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages.base import BaseMessage
from app.core.database import delete_document, get_document, update_document, insert_document, get_mongodb_conn
from app.classes.conversation import Conversation, ConversationInfo

CONVERSATION_COLLECTION = "conversation"

class MongoDBChatHistory(BaseChatMessageHistory):
    def __init__(self, session_id: str):
        self._session_id = session_id

    async def _aget_conversation(self) -> Conversation | None:
        if self._session_id == "":
            await self._acreate_new_conversation()
        
        data = await get_document(CONVERSATION_COLLECTION, self._session_id)
        if not data:
            return None
        
        # Deserialize message dictionaries back to proper BaseMessage subclasses
        raw_messages = data.get("messages", [])
        messages = []
        
        for msg_data in raw_messages:
            if isinstance(msg_data, dict):
                msg_type = msg_data.get('type', 'human')  # Default to human if type not specified
                content = msg_data.get('content', '')
                
                if msg_type == 'human':
                    messages.append(HumanMessage(content=content))
                elif msg_type == 'ai':
                    messages.append(AIMessage(content=content))
                elif msg_type == 'system':
                    messages.append(SystemMessage(content=content))
                else:
                    # Fallback to HumanMessage for unknown types
                    messages.append(HumanMessage(content=content))
            else:
                # Fallback: treat as string content for HumanMessage
                messages.append(HumanMessage(content=str(msg_data)))
        
        return Conversation(
            id=str(data.get("_id", "")),
            name=data.get("name", ""),
            messages=messages,
            created_at=data.get("created_at", datetime.now(timezone.utc)),
            updated_at=data.get("updated_at", datetime.now(timezone.utc))
        )

    @property
    def messages(self) -> list[BaseMessage]:
        return asyncio.run(self.aget_messages())
    
    async def _acreate_new_conversation(self) -> None:
        session_id = await insert_document(CONVERSATION_COLLECTION, {
                "name": "",
                "messages": [],
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            })
        self._session_id = session_id
        
    async def aget_messages(self) -> list[BaseMessage]:
        conversation = await self._aget_conversation()
        if not conversation:
            return []
        # Type cast to satisfy type checker - messages are already BaseMessage subclasses
        return list(conversation.messages)
    
    def add_messages(self, messages: Sequence[BaseMessage]) -> None:
        asyncio.run(self.aadd_messages(messages))

    async def aadd_messages(self, messages: Sequence[BaseMessage]) -> None:
        if self._session_id == "":
            await self._acreate_new_conversation()

        all_messages = await self.aget_messages()
        all_messages.extend(messages)

        # Serialize messages properly for storage
        serialized_messages = []
        for message in all_messages:
            serialized_messages.append(message.model_dump())

        await update_document(CONVERSATION_COLLECTION, self._session_id, {
            "updated_at": datetime.now(timezone.utc),
            "messages": serialized_messages
        })

    def clear(self) -> None:
        asyncio.run(self.aclear())

    async def aclear(self) -> None:
        await update_document(CONVERSATION_COLLECTION, self._session_id, {
            "updated_at": datetime.now(timezone.utc),
            "messages": []
        })

class ConversationRepository:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance") or cls._instance is None:
            cls._instance = super(ConversationRepository, cls).__new__(cls)
        return cls._instance

    async def get_conversations(self, limit: int) -> list[ConversationInfo]:
        """
        Retrieve the latest n conversations from MongoDB, sorted by updated_at in descending order.
        
        Args:
            limit: Maximum number of conversations to retrieve
            
        Returns:
            List of ConversationInfo objects
        """
        try:
            db = get_mongodb_conn()
            
            # Query conversations, sort by updated_at desc, limit results
            cursor = db[CONVERSATION_COLLECTION].find(
                {},  # No filter - get all conversations
                {"_id": 1, "name": 1, "updated_at": 1}
            ).sort("updated_at", -1).limit(limit)
            
            conversations = []
            async for doc in cursor:
                conversation_info = ConversationInfo(
                    session_id=str(doc["_id"]),
                    name=doc.get("name", ""),
                    updated_at=doc["updated_at"]
                )
                conversations.append(conversation_info)
            
            return conversations
            
        except Exception as e:
            logging.getLogger("uvicorn.error").error(f"Error retrieving conversations: {e}")
            return []
        
    async def get_conversation(self, id: str) -> Conversation | None:
        """
        Retrieve a conversation by its ID.
        
        Args:
            id: The ID of the conversation to retrieve
            
        Returns:
            Conversation object if found, None otherwise
        """
        try:
            data = await get_document(CONVERSATION_COLLECTION, id)
            if not data:
                return None
            
            # Deserialize message dictionaries back to proper BaseMessage subclasses
            raw_messages = data.get("messages", [])
            deserialized_messages = []
            
            for msg_data in raw_messages:
                if isinstance(msg_data, dict):
                    # Determine message type and create appropriate instance
                    msg_type = msg_data.get('type', 'human')  # Default to human if type not specified
                    content = msg_data.get('content', '')
                    
                    if msg_type == 'human':
                        deserialized_messages.append(HumanMessage(content=content))
                    elif msg_type == 'ai':
                        deserialized_messages.append(AIMessage(content=content))
                    elif msg_type == 'system':
                        deserialized_messages.append(SystemMessage(content=content))
                    else:
                        # Fallback to HumanMessage for unknown types
                        deserialized_messages.append(HumanMessage(content=content))
                elif isinstance(msg_data, BaseMessage):
                    # Already a proper BaseMessage instance
                    deserialized_messages.append(msg_data)
                else:
                    # Fallback: treat as string content for HumanMessage
                    deserialized_messages.append(HumanMessage(content=str(msg_data)))
            
            return Conversation(
                id=str(data.get("_id", "")),
                name=data.get("name", ""),
                messages=deserialized_messages,
                created_at=data.get("created_at", datetime.now(timezone.utc)),
                updated_at=data.get("updated_at", datetime.now(timezone.utc))
            )
            
        except Exception as e:
            logging.getLogger("uvicorn.error").error(f"Error retrieving conversation: {e}")
            return None
        
    async def delete_conversation(self, id: str) -> bool:
        """
        Delete a conversation by its ID.
        
        Args:
            id: The ID of the conversation to delete
            
        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            await delete_document(CONVERSATION_COLLECTION, id)
            return True
        except Exception as e:
            logging.getLogger("uvicorn.error").error(f"Error deleting conversation: {e}")
            return False
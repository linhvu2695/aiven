import asyncio
from datetime import datetime, timezone
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages.base import BaseMessage
from app.core.database import get_document, update_document, insert_document
from app.classes.conversation import Conversation
from collections.abc import Sequence

CONVERSATION_COLLECTION = "conversation"

class MongoDBChatHistory(BaseChatMessageHistory):
    def __init__(self, session_id: str):
        self._session_id = session_id

    async def _aget_conversation(self) -> Conversation | None:
        data = await get_document(CONVERSATION_COLLECTION, self._session_id)
        if not data:
            return None
        
        return Conversation(
            id=str(data.get("_id", "")),
            messages=data.get("messages", []),
            created_at=data.get("created_at", datetime.now(timezone.utc)),
            updated_at=data.get("updated_at", datetime.now(timezone.utc))
        )

    @property
    def messages(self) -> list[BaseMessage]:
        return asyncio.run(self.aget_messages())
    
    async def aget_messages(self) -> list[BaseMessage]:
        conversation = await self._aget_conversation()
        if not conversation:
            return []
        return conversation.messages
    
    def add_messages(self, messages: Sequence[BaseMessage]) -> None:
        asyncio.run(self.aadd_messages(messages))

    async def aadd_messages(self, messages: Sequence[BaseMessage]) -> None:
        if self._session_id == "":
            # Create new empty conversation
            session_id = await insert_document(CONVERSATION_COLLECTION, {
                "messages": [],
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            })
            self._session_id = session_id

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


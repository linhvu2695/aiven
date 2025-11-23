import pytest
from unittest.mock import patch, AsyncMock, MagicMock, ANY
from datetime import datetime, timezone
from bson import ObjectId
from langchain_core.messages import HumanMessage, AIMessage

from app.services.chat.chat_history import MongoDBChatHistory, CONVERSATION_COLLECTION
from app.classes.conversation import Conversation

# Test constants
TEST_SESSION_ID = "test-session-id"
TEST_NEW_SESSION_ID = "test-new-session-id"
TEST_PERSISTENT_SESSION_ID = "test-persistent-session-id"
TEST_AGENT_ID = "test-agent-id"
TEST_OBJECT_ID = ObjectId("507f1f77bcf86cd799439011")  # Valid ObjectId for testing


@pytest.fixture
def sample_messages():
    """Sample messages for testing."""
    return [
        HumanMessage(content="Hello, how are you?"),
        AIMessage(content="I'm doing well, thank you for asking!"),
        HumanMessage(content="What's the weather like?")
    ]


@pytest.fixture
def sample_serialized_messages():
    """Sample serialized messages for testing."""
    return [
        {"content": "Hello, how are you?", "type": "human"},
        {"content": "I'm doing well, thank you for asking!", "type": "ai"},
        {"content": "What's the weather like?", "type": "human"}
    ]


@pytest.fixture
def sample_conversation_data():
    """Sample conversation data from database."""
    return {
        "_id": TEST_OBJECT_ID,
        "messages": [
            {"content": "Hello, how are you?", "type": "human"},
            {"content": "I'm doing well, thank you for asking!", "type": "ai"}
        ],
        "agent_id": TEST_AGENT_ID,
        "created_at": datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
        "updated_at": datetime(2023, 1, 1, 12, 5, 0, tzinfo=timezone.utc)
    }


class TestMongoDBChatHistoryInitialization:
    """Test MongoDBChatHistory initialization."""
    
    def test_init_with_session_id(self):
        """Test initialization with a session ID."""
        chat_history = MongoDBChatHistory(TEST_SESSION_ID)
        
        assert chat_history._session_id == TEST_SESSION_ID
    
    def test_init_with_empty_session_id(self):
        """Test initialization with empty session ID."""
        chat_history = MongoDBChatHistory("")
        
        assert chat_history._session_id == ""
    
    def test_init_with_agent_id(self):
        """Test initialization with agent ID."""
        chat_history = MongoDBChatHistory(TEST_SESSION_ID, TEST_AGENT_ID)
        
        assert chat_history._session_id == TEST_SESSION_ID
        assert chat_history._agent_id == TEST_AGENT_ID
    
    def test_init_with_default_agent_id(self):
        """Test initialization with default empty agent ID."""
        chat_history = MongoDBChatHistory(TEST_SESSION_ID)
        
        assert chat_history._session_id == TEST_SESSION_ID
        assert chat_history._agent_id == ""


class TestGetConversation:
    """Test _aget_conversation method."""
    
    @pytest.mark.asyncio
    @patch('app.services.chat.chat_history.MongoDB')
    async def test_aget_conversation_exists(self, mock_mongodb_class, sample_conversation_data):
        """Test getting an existing conversation."""
        mock_mongodb_instance = MagicMock()
        mock_mongodb_class.return_value = mock_mongodb_instance
        mock_mongodb_instance.get_document = AsyncMock(return_value=sample_conversation_data)
        
        chat_history = MongoDBChatHistory(TEST_SESSION_ID)
        conversation = await chat_history._aget_conversation()
        
        mock_mongodb_instance.get_document.assert_called_once_with(CONVERSATION_COLLECTION, TEST_SESSION_ID)
        assert conversation is not None
        assert conversation.id == str(sample_conversation_data["_id"])
        assert len(conversation.messages) == 2
        assert conversation.created_at == sample_conversation_data["created_at"]
        assert conversation.updated_at == sample_conversation_data["updated_at"]
    
    @pytest.mark.asyncio
    @patch('app.services.chat.chat_history.MongoDB')
    async def test_aget_conversation_not_exists(self, mock_mongodb_class):
        """Test getting a non-existent conversation."""
        mock_mongodb_instance = MagicMock()
        mock_mongodb_class.return_value = mock_mongodb_instance
        mock_mongodb_instance.get_document = AsyncMock(return_value=None)
        
        chat_history = MongoDBChatHistory("nonexistent_session")
        conversation = await chat_history._aget_conversation()
        
        mock_mongodb_instance.get_document.assert_called_once_with(CONVERSATION_COLLECTION, "nonexistent_session")
        assert conversation is None
    
    @pytest.mark.asyncio
    @patch('app.services.chat.chat_history.MongoDB')
    async def test_aget_conversation_empty_data(self, mock_mongodb_class):
        """Test getting conversation with minimal data."""
        mock_mongodb_instance = MagicMock()
        mock_mongodb_class.return_value = mock_mongodb_instance
        mock_mongodb_instance.get_document = AsyncMock(return_value={"_id": TEST_OBJECT_ID})
        
        chat_history = MongoDBChatHistory(TEST_SESSION_ID)
        conversation = await chat_history._aget_conversation()
        
        assert conversation is not None
        assert conversation.messages == []
        assert isinstance(conversation.created_at, datetime)
        assert isinstance(conversation.updated_at, datetime)


class TestGetMessages:
    """Test aget_messages and messages methods."""
    
    @pytest.mark.asyncio
    @patch('app.services.chat.chat_history.MongoDB')
    async def test_aget_messages_with_conversation(self, mock_mongodb_class, sample_conversation_data):
        """Test getting messages from existing conversation."""
        mock_mongodb_instance = MagicMock()
        mock_mongodb_class.return_value = mock_mongodb_instance
        mock_mongodb_instance.get_document = AsyncMock(return_value=sample_conversation_data)
        
        chat_history = MongoDBChatHistory(TEST_SESSION_ID)
        messages = await chat_history.aget_messages()
        
        assert len(messages) == 2
        # Messages are deserialized back to BaseMessage objects
        assert all(hasattr(msg, 'content') for msg in messages)
    
    @pytest.mark.asyncio
    @patch('app.services.chat.chat_history.MongoDB')
    async def test_aget_messages_no_conversation(self, mock_mongodb_class):
        """Test getting messages when no conversation exists."""
        mock_mongodb_instance = MagicMock()
        mock_mongodb_class.return_value = mock_mongodb_instance
        mock_mongodb_instance.get_document = AsyncMock(return_value=None)
        
        chat_history = MongoDBChatHistory(TEST_SESSION_ID)
        messages = await chat_history.aget_messages()
        
        assert messages == []
    
    @patch('app.services.chat.chat_history.MongoDB')
    def test_messages_property(self, mock_mongodb_class, sample_conversation_data):
        """Test the synchronous messages property."""
        mock_mongodb_instance = MagicMock()
        mock_mongodb_class.return_value = mock_mongodb_instance
        mock_mongodb_instance.get_document = AsyncMock(return_value=sample_conversation_data)
        
        chat_history = MongoDBChatHistory(TEST_SESSION_ID)
        messages = chat_history.messages
        
        assert len(messages) == 2
        assert all(hasattr(msg, 'content') for msg in messages)


class TestAddMessages:
    """Test aadd_messages and add_messages methods."""
    
    @pytest.mark.asyncio
    @patch('app.services.chat.chat_history.update_document')
    @patch('app.services.chat.chat_history.MongoDB')
    async def test_aadd_messages_existing_conversation(
        self, mock_mongodb_class, mock_update_document, sample_conversation_data, sample_messages
    ):
        """Test adding messages to existing conversation."""
        mock_mongodb_instance = MagicMock()
        mock_mongodb_class.return_value = mock_mongodb_instance
        mock_mongodb_instance.get_document = AsyncMock(return_value=sample_conversation_data)
        
        chat_history = MongoDBChatHistory(TEST_SESSION_ID)
        await chat_history.aadd_messages([sample_messages[2]])  # Add third message
        
        # Verify update_document was called with correct parameters
        mock_update_document.assert_called_once()
        call_args = mock_update_document.call_args
        assert call_args[0][0] == CONVERSATION_COLLECTION
        assert call_args[0][1] == TEST_SESSION_ID
        
        update_data = call_args[0][2]
        assert "updated_at" in update_data
        assert "messages" in update_data
        assert len(update_data["messages"]) == 3  # Original 2 + 1 new
    
    @pytest.mark.asyncio
    @patch('app.services.chat.chat_history.update_document')
    @patch('app.services.chat.chat_history.insert_document')
    @patch('app.services.chat.chat_history.MongoDB')
    async def test_aadd_messages_new_conversation(
        self, mock_mongodb_class, mock_insert_document, mock_update_document, sample_messages
    ):
        """Test adding messages when creating new conversation."""
        mock_mongodb_instance = MagicMock()
        mock_mongodb_class.return_value = mock_mongodb_instance
        mock_mongodb_instance.get_document = AsyncMock(return_value=None)
        mock_insert_document.return_value = TEST_NEW_SESSION_ID
        
        chat_history = MongoDBChatHistory("", TEST_AGENT_ID)  # Empty session ID with agent ID
        await chat_history.aadd_messages([sample_messages[0]])
        
        # Verify new conversation was created
        mock_insert_document.assert_called_once()
        insert_args = mock_insert_document.call_args[0]
        assert insert_args[0] == CONVERSATION_COLLECTION
        assert insert_args[1]["messages"] == []
        assert insert_args[1]["agent_id"] == TEST_AGENT_ID
        assert "created_at" in insert_args[1]
        assert "updated_at" in insert_args[1]
        
        # Verify session ID was updated
        assert chat_history._session_id == TEST_NEW_SESSION_ID
        
        # Verify messages were updated
        mock_update_document.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('app.services.chat.chat_history.update_document')
    @patch('app.services.chat.chat_history.MongoDB')
    async def test_aadd_messages_multiple(
        self, mock_mongodb_class, mock_update_document, sample_messages
    ):
        """Test adding multiple messages at once."""
        mock_mongodb_instance = MagicMock()
        mock_mongodb_class.return_value = mock_mongodb_instance
        mock_mongodb_instance.get_document = AsyncMock(return_value={"_id": TEST_OBJECT_ID, "messages": []})
        
        chat_history = MongoDBChatHistory(TEST_SESSION_ID)
        await chat_history.aadd_messages(sample_messages[:2])  # Add first two messages
        
        mock_update_document.assert_called_once()
        call_args = mock_update_document.call_args
        update_data = call_args[0][2]
        assert len(update_data["messages"]) == 2
    
    @patch('app.services.chat.chat_history.update_document')
    @patch('app.services.chat.chat_history.MongoDB')
    def test_add_messages_sync(self, mock_mongodb_class, mock_update_document, sample_messages):
        """Test the synchronous add_messages method."""
        mock_mongodb_instance = MagicMock()
        mock_mongodb_class.return_value = mock_mongodb_instance
        mock_mongodb_instance.get_document = AsyncMock(return_value={"_id": TEST_OBJECT_ID, "messages": []})
        
        chat_history = MongoDBChatHistory(TEST_SESSION_ID)
        chat_history.add_messages([sample_messages[0]])
        
        # Should have called the async version
        mock_update_document.assert_called_once()


class TestClearMessages:
    """Test aclear and clear methods."""
    
    @pytest.mark.asyncio
    @patch('app.services.chat.chat_history.update_document')
    async def test_aclear(self, mock_update_document):
        """Test clearing messages asynchronously."""
        chat_history = MongoDBChatHistory(TEST_SESSION_ID)
        await chat_history.aclear()
        
        mock_update_document.assert_called_once_with(
            CONVERSATION_COLLECTION,
            TEST_SESSION_ID,
            {
                "updated_at": ANY,
                "messages": []
            }
        )
    
    @patch('app.services.chat.chat_history.update_document')
    def test_clear_sync(self, mock_update_document):
        """Test clearing messages synchronously."""
        chat_history = MongoDBChatHistory(TEST_SESSION_ID)
        chat_history.clear()
        
        # Should have called the async version
        mock_update_document.assert_called_once()


class TestEdgeCases:
    """Test edge cases and error scenarios."""
    
    @pytest.mark.asyncio
    @patch('app.services.chat.chat_history.MongoDB')
    async def test_empty_messages_list(self, mock_mongodb_class):
        """Test handling empty messages list."""
        mock_mongodb_instance = MagicMock()
        mock_mongodb_class.return_value = mock_mongodb_instance
        mock_mongodb_instance.get_document = AsyncMock(return_value={"_id": TEST_OBJECT_ID, "messages": []})
        
        chat_history = MongoDBChatHistory(TEST_SESSION_ID)
        messages = await chat_history.aget_messages()
        
        assert messages == []
    
    @pytest.mark.asyncio
    @patch('app.services.chat.chat_history.update_document')
    @patch('app.services.chat.chat_history.MongoDB')
    async def test_add_empty_messages_list(self, mock_mongodb_class, mock_update_document):
        """Test adding empty list of messages."""
        mock_mongodb_instance = MagicMock()
        mock_mongodb_class.return_value = mock_mongodb_instance
        mock_mongodb_instance.get_document = AsyncMock(return_value={"_id": TEST_OBJECT_ID, "messages": []})
        
        chat_history = MongoDBChatHistory(TEST_SESSION_ID)
        await chat_history.aadd_messages([])
        
        # Should still update the document
        mock_update_document.assert_called_once()
        call_args = mock_update_document.call_args
        update_data = call_args[0][2]
        assert update_data["messages"] == []
    
    @pytest.mark.asyncio
    @patch('app.services.chat.chat_history.MongoDB')
    async def test_malformed_conversation_data(self, mock_mongodb_class):
        """Test handling malformed conversation data."""
        mock_mongodb_instance = MagicMock()
        mock_mongodb_class.return_value = mock_mongodb_instance
        # Missing required fields
        mock_mongodb_instance.get_document = AsyncMock(return_value={"some_field": "some_value"})
        
        chat_history = MongoDBChatHistory(TEST_SESSION_ID)
        conversation = await chat_history._aget_conversation()
        
        # Should handle missing fields gracefully
        assert conversation is not None
        assert conversation.id == ""  # Missing _id becomes empty string
        assert conversation.messages == []  # Missing messages becomes empty list
    
    def test_session_id_persistence(self):
        """Test that session ID is properly stored and accessible."""
        chat_history = MongoDBChatHistory(TEST_PERSISTENT_SESSION_ID)
        
        assert chat_history._session_id == TEST_PERSISTENT_SESSION_ID
        
        # Session ID should remain the same throughout object lifecycle
        assert chat_history._session_id == TEST_PERSISTENT_SESSION_ID


class TestIntegration:
    """Integration-style tests that test multiple methods together."""
    
    @pytest.mark.asyncio
    @patch('app.services.chat.chat_history.update_document')
    @patch('app.services.chat.chat_history.MongoDB')
    async def test_full_conversation_flow(
        self, mock_mongodb_class, mock_update_document, sample_messages
    ):
        """Test a complete conversation flow: create, add messages, get messages, clear."""
        mock_mongodb_instance = MagicMock()
        mock_mongodb_class.return_value = mock_mongodb_instance
        
        # Start with empty conversation
        mock_mongodb_instance.get_document = AsyncMock(return_value={"_id": TEST_OBJECT_ID, "messages": []})
        
        chat_history = MongoDBChatHistory(TEST_SESSION_ID)
        
        # Add first message
        await chat_history.aadd_messages([sample_messages[0]])
        
        # Simulate database now has the message
        mock_mongodb_instance.get_document = AsyncMock(return_value={
            "_id": TEST_OBJECT_ID,
            "messages": [sample_messages[0].model_dump()]
        })
        
        # Get messages
        messages = await chat_history.aget_messages()
        assert len(messages) == 1
        
        # Clear messages
        await chat_history.aclear()
        
        # Verify all operations called update_document
        assert mock_update_document.call_count == 2  # Once for add, once for clear
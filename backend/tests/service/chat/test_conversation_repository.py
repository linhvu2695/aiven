import pytest
from unittest.mock import patch, AsyncMock, MagicMock, ANY
from datetime import datetime, timezone
from bson import ObjectId

from app.services.chat.chat_history import ConversationRepository, CONVERSATION_COLLECTION
from app.classes.conversation import Conversation, ConversationInfo

# Test constants
TEST_SESSION_ID = "test-session-id"
TEST_SESSION_ID_2 = "test-session-id-2"
TEST_OBJECT_ID = ObjectId("507f1f77bcf86cd799439011")
TEST_OBJECT_ID_2 = ObjectId("507f1f77bcf86cd799439012")


@pytest.fixture
def sample_conversation_data():
    """Sample conversation data from database."""
    return {
        "_id": TEST_OBJECT_ID,
        "name": "Test Conversation",
        "messages": [
            {"content": "Hello", "type": "human"},
            {"content": "Hi there!", "type": "ai"}
        ],
        "created_at": datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
        "updated_at": datetime(2023, 1, 1, 12, 5, 0, tzinfo=timezone.utc)
    }


@pytest.fixture
def sample_conversation_info_data():
    """Sample conversation info data for list queries."""
    return [
        {
            "_id": TEST_OBJECT_ID,
            "name": "Recent Conversation",
            "updated_at": datetime(2023, 1, 2, 12, 0, 0, tzinfo=timezone.utc)
        },
        {
            "_id": TEST_OBJECT_ID_2,
            "name": "Older Conversation", 
            "updated_at": datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        }
    ]


class TestConversationRepositorySingleton:
    """Test ConversationRepository singleton pattern."""
    
    def test_singleton_same_instance(self):
        """Test that multiple instantiations return the same instance."""
        repo1 = ConversationRepository()
        repo2 = ConversationRepository()
        
        assert repo1 is repo2
        assert id(repo1) == id(repo2)
    
    def test_singleton_with_args(self):
        """Test that singleton works even with different args."""
        repo1 = ConversationRepository()
        repo2 = ConversationRepository("some", "args")
        
        assert repo1 is repo2


class TestGetConversations:
    """Test get_conversations method."""
    
    @pytest.mark.asyncio
    @patch('app.services.chat.chat_history.get_mongodb_conn')
    async def test_get_conversations_success(self, mock_get_conn, sample_conversation_info_data):
        """Test successful retrieval of conversations."""
        # Mock database connection and cursor
        mock_db = MagicMock()
        mock_collection = MagicMock()
        mock_cursor = MagicMock()
        
        mock_get_conn.return_value = mock_db
        mock_db.__getitem__.return_value = mock_collection
        mock_collection.find.return_value = mock_cursor
        mock_cursor.sort.return_value = mock_cursor
        mock_cursor.limit.return_value = mock_cursor
        
        # Mock async iteration properly
        async def mock_async_iter(self):
            for doc in sample_conversation_info_data:
                yield doc
        
        mock_cursor.__aiter__ = mock_async_iter
        
        repo = ConversationRepository()
        conversations = await repo.get_conversations(limit=10)
        
        # Verify the correct database query was made
        mock_collection.find.assert_called_once_with(
            {},  # No filter
            {"_id": 1, "name": 1, "updated_at": 1}
        )
        mock_cursor.sort.assert_called_once_with("updated_at", -1)
        mock_cursor.limit.assert_called_once_with(10)
        
        # Verify results
        assert len(conversations) == 2
        assert all(isinstance(conv, ConversationInfo) for conv in conversations)
        assert conversations[0].session_id == str(TEST_OBJECT_ID)
        assert conversations[0].name == "Recent Conversation"
        assert conversations[1].session_id == str(TEST_OBJECT_ID_2)
        assert conversations[1].name == "Older Conversation"
    
    @pytest.mark.asyncio
    @patch('app.services.chat.chat_history.get_mongodb_conn')
    async def test_get_conversations_empty_result(self, mock_get_conn):
        """Test retrieval when no conversations exist."""
        mock_db = MagicMock()
        mock_collection = MagicMock()
        mock_cursor = MagicMock()
        
        mock_get_conn.return_value = mock_db
        mock_db.__getitem__.return_value = mock_collection
        mock_collection.find.return_value = mock_cursor
        mock_cursor.sort.return_value = mock_cursor
        mock_cursor.limit.return_value = mock_cursor
        
        # Mock empty async iteration
        async def mock_empty_iter(self):
            return
            yield  # This line will never be reached
        
        mock_cursor.__aiter__ = mock_empty_iter
        
        repo = ConversationRepository()
        conversations = await repo.get_conversations(limit=10)
        
        assert conversations == []
    
    @pytest.mark.asyncio
    @patch('app.services.chat.chat_history.get_mongodb_conn')
    @patch('logging.getLogger')
    async def test_get_conversations_database_error(self, mock_get_logger, mock_get_conn):
        """Test error handling when database operation fails."""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        # Mock database connection to raise an exception
        mock_get_conn.side_effect = Exception("Database connection failed")
        
        repo = ConversationRepository()
        conversations = await repo.get_conversations(limit=10)
        
        # Should return empty list on error
        assert conversations == []
        
        # Should log the error
        mock_logger.error.assert_called_once()
        assert "Error retrieving conversations" in mock_logger.error.call_args[0][0]
    
    @pytest.mark.asyncio
    @patch('app.services.chat.chat_history.get_mongodb_conn')
    async def test_get_conversations_with_different_limits(self, mock_get_conn):
        """Test that different limit values are passed correctly."""
        mock_db = MagicMock()
        mock_collection = MagicMock()
        mock_cursor = MagicMock()
        
        mock_get_conn.return_value = mock_db
        mock_db.__getitem__.return_value = mock_collection
        mock_collection.find.return_value = mock_cursor
        mock_cursor.sort.return_value = mock_cursor
        mock_cursor.limit.return_value = mock_cursor
        
        async def mock_empty_iter(self):
            return
            yield
        
        mock_cursor.__aiter__ = mock_empty_iter
        
        repo = ConversationRepository()
        
        # Test different limits
        await repo.get_conversations(limit=5)
        mock_cursor.limit.assert_called_with(5)
        
        await repo.get_conversations(limit=20)
        mock_cursor.limit.assert_called_with(20)
    
    @pytest.mark.asyncio
    @patch('app.services.chat.chat_history.get_mongodb_conn')
    async def test_get_conversations_missing_name_field(self, mock_get_conn):
        """Test handling of documents with missing name field."""
        mock_db = MagicMock()
        mock_collection = MagicMock()
        mock_cursor = MagicMock()
        
        mock_get_conn.return_value = mock_db
        mock_db.__getitem__.return_value = mock_collection
        mock_collection.find.return_value = mock_cursor
        mock_cursor.sort.return_value = mock_cursor
        mock_cursor.limit.return_value = mock_cursor
        
        # Document without name field
        conversation_without_name = {
            "_id": TEST_OBJECT_ID,
            "updated_at": datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        }
        
        async def mock_async_iter(self):
            yield conversation_without_name
        
        mock_cursor.__aiter__ = mock_async_iter
        
        repo = ConversationRepository()
        conversations = await repo.get_conversations(limit=10)
        
        assert len(conversations) == 1
        assert conversations[0].name == ""  # Should default to empty string


class TestGetConversation:
    """Test get_conversation method."""
    
    @pytest.mark.asyncio
    @patch('app.services.chat.chat_history.get_document')
    async def test_get_conversation_success(self, mock_get_document, sample_conversation_data):
        """Test successful retrieval of a specific conversation."""
        mock_get_document.return_value = sample_conversation_data
        
        repo = ConversationRepository()
        conversation = await repo.get_conversation(TEST_SESSION_ID)
        
        mock_get_document.assert_called_once_with(CONVERSATION_COLLECTION, TEST_SESSION_ID)
        
        assert conversation is not None
        assert isinstance(conversation, Conversation)
        assert conversation.id == str(TEST_OBJECT_ID)
        assert conversation.name == "Test Conversation"
        assert len(conversation.messages) == 2
        assert conversation.created_at == sample_conversation_data["created_at"]
        assert conversation.updated_at == sample_conversation_data["updated_at"]
    
    @pytest.mark.asyncio
    @patch('app.services.chat.chat_history.get_document')
    async def test_get_conversation_not_found(self, mock_get_document):
        """Test retrieval of non-existent conversation."""
        mock_get_document.return_value = None
        
        repo = ConversationRepository()
        conversation = await repo.get_conversation("nonexistent-id")
        
        mock_get_document.assert_called_once_with(CONVERSATION_COLLECTION, "nonexistent-id")
        assert conversation is None
    
    @pytest.mark.asyncio
    @patch('app.services.chat.chat_history.get_document')
    async def test_get_conversation_minimal_data(self, mock_get_document):
        """Test handling of conversation with minimal data."""
        minimal_data = {"_id": TEST_OBJECT_ID}
        mock_get_document.return_value = minimal_data
        
        repo = ConversationRepository()
        conversation = await repo.get_conversation(TEST_SESSION_ID)
        
        assert conversation is not None
        assert conversation.id == str(TEST_OBJECT_ID)
        assert conversation.name == ""  # Should default to empty string
        assert conversation.messages == []  # Should default to empty list
        assert isinstance(conversation.created_at, datetime)
        assert isinstance(conversation.updated_at, datetime)
    
    @pytest.mark.asyncio
    @patch('app.services.chat.chat_history.get_document')
    @patch('logging.getLogger')
    async def test_get_conversation_database_error(self, mock_get_logger, mock_get_document):
        """Test error handling when get_document fails."""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        mock_get_document.side_effect = Exception("Database error")
        
        repo = ConversationRepository()
        conversation = await repo.get_conversation(TEST_SESSION_ID)
        
        # Should return None on error
        assert conversation is None
        
        # Should log the error
        mock_logger.error.assert_called_once()
        assert "Error retrieving conversation" in mock_logger.error.call_args[0][0]
    
    @pytest.mark.asyncio
    @patch('app.services.chat.chat_history.get_document')
    async def test_get_conversation_missing_fields(self, mock_get_document):
        """Test handling of conversation data with missing optional fields."""
        data_missing_fields = {
            "_id": TEST_OBJECT_ID,
            # Missing name, messages, created_at, updated_at
        }
        mock_get_document.return_value = data_missing_fields
        
        repo = ConversationRepository()
        conversation = await repo.get_conversation(TEST_SESSION_ID)
        
        assert conversation is not None
        assert conversation.id == str(TEST_OBJECT_ID)
        assert conversation.name == ""
        assert conversation.messages == []
        # Timestamps should be set to current time when missing
        assert isinstance(conversation.created_at, datetime)
        assert isinstance(conversation.updated_at, datetime)

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from bson import ObjectId
from bson.errors import InvalidId

from app.core.database import (
    get_mongodb_conn,
    check_mongodb_health,
    get_document,
    insert_document,
    update_document,
    list_documents,
    find_documents_by_field,
    delete_document
)

@pytest.fixture
def mock_motor_client():
    """Mock the MongoDB motor client and database"""
    with patch("app.core.database.AsyncIOMotorClient") as MockClient:
        mock_client_instance = MagicMock()
        MockClient.return_value = mock_client_instance
        
        mock_db = MagicMock()
        mock_client_instance.get_database.return_value = mock_db
        
        # Mock collection methods
        mock_collection = MagicMock()
        mock_db.__getitem__.return_value = mock_collection
        
        # Mock async database methods
        mock_collection.find_one = AsyncMock()
        mock_collection.insert_one = AsyncMock()
        mock_collection.update_one = AsyncMock()
        mock_collection.delete_one = AsyncMock()
        mock_collection.find = MagicMock()
        mock_db.command = AsyncMock()
        
        yield {
            "client": MockClient,
            "db": mock_db,
            "collection": mock_collection
        }

class TestGetMongodbConn:
    @patch("app.core.database.settings")
    def test_get_mongodb_conn_creates_correct_uri(self, mock_settings, mock_motor_client):
        """Test that _get_mongodb_conn creates the correct MongoDB URI"""
        # Arrange
        mock_settings.mongodb_host = "localhost"
        mock_settings.mongodb_port = 27017
        mock_settings.mongodb_root_username = "admin"
        mock_settings.mongodb_root_password = "password"
        mock_settings.mongodb_db_name = "testdb"
        
        # Act
        result = get_mongodb_conn()
        
        # Assert
        expected_uri = "mongodb://admin:password@localhost:27017"
        mock_motor_client["client"].assert_called_once_with(expected_uri)
        mock_motor_client["client"].return_value.get_database.assert_called_once_with("testdb")
        assert result == mock_motor_client["db"]

class TestCheckMongodbHealth:
    @pytest.mark.asyncio
    async def test_check_mongodb_health_success(self, mock_motor_client):
        """Test successful MongoDB health check"""
        # Arrange
        mock_motor_client["db"].command.return_value = {"ok": 1}
        
        # Act
        result = await check_mongodb_health()
        
        # Assert
        assert result is True
        mock_motor_client["db"].command.assert_awaited_once_with("ping")

    @pytest.mark.asyncio
    async def test_check_mongodb_health_failure(self, mock_motor_client):
        """Test MongoDB health check failure"""
        # Arrange
        mock_motor_client["db"].command.side_effect = Exception("Connection failed")
        
        # Act
        result = await check_mongodb_health()
        
        # Assert
        assert result is False
        mock_motor_client["db"].command.assert_awaited_once_with("ping")

class TestGetDocument:
    @pytest.mark.asyncio
    async def test_get_document_success(self, mock_motor_client):
        """Test successful document retrieval"""
        # Arrange
        doc_id = str(ObjectId())
        expected_doc = {"_id": ObjectId(doc_id), "name": "test"}
        mock_motor_client["collection"].find_one.return_value = expected_doc
        
        # Act
        result = await get_document("test_collection", doc_id)
        
        # Assert
        assert result == expected_doc
        mock_motor_client["collection"].find_one.assert_awaited_once_with({"_id": ObjectId(doc_id)})

    @pytest.mark.asyncio
    async def test_get_document_not_found(self, mock_motor_client):
        """Test document not found scenario"""
        # Arrange
        doc_id = str(ObjectId())
        mock_motor_client["collection"].find_one.return_value = None
        
        # Act & Assert
        with pytest.raises(ValueError, match="Document not found"):
            await get_document("test_collection", doc_id)

    @pytest.mark.asyncio
    async def test_get_document_invalid_id(self, mock_motor_client):
        """Test invalid document ID format"""
        # Arrange
        invalid_id = "invalid_id"
        
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid document id format"):
            await get_document("test_collection", invalid_id)

class TestInsertDocument:
    @pytest.mark.asyncio
    async def test_insert_document_success(self, mock_motor_client):
        """Test successful document insertion"""
        # Arrange
        document = {"name": "test", "value": 123}
        inserted_id = ObjectId()
        mock_result = MagicMock()
        mock_result.inserted_id = inserted_id
        mock_motor_client["collection"].insert_one.return_value = mock_result
        
        # Act
        result = await insert_document("test_collection", document)
        
        # Assert
        assert result == str(inserted_id)
        mock_motor_client["collection"].insert_one.assert_awaited_once_with(document)

class TestUpdateDocument:
    @pytest.mark.asyncio
    async def test_update_document_existing(self, mock_motor_client):
        """Test updating an existing document"""
        # Arrange
        doc_id = str(ObjectId())
        document = {"name": "updated"}
        mock_result = MagicMock()
        mock_result.upserted_id = None  # No upsert, document existed
        mock_motor_client["collection"].update_one.return_value = mock_result
        
        # Act
        result = await update_document("test_collection", doc_id, document)
        
        # Assert
        assert result is None
        mock_motor_client["collection"].update_one.assert_awaited_once_with(
            {"_id": ObjectId(doc_id)},
            {"$set": document},
            upsert=True
        )

    @pytest.mark.asyncio
    async def test_update_document_upsert(self, mock_motor_client):
        """Test upserting a new document"""
        # Arrange
        doc_id = str(ObjectId())
        document = {"name": "new"}
        upserted_id = ObjectId()
        mock_result = MagicMock()
        mock_result.upserted_id = upserted_id
        mock_motor_client["collection"].update_one.return_value = mock_result
        
        # Act
        result = await update_document("test_collection", doc_id, document)
        
        # Assert
        assert result == upserted_id
        mock_motor_client["collection"].update_one.assert_awaited_once_with(
            {"_id": ObjectId(doc_id)},
            {"$set": document},
            upsert=True
        )

class TestListDocuments:
    @pytest.mark.asyncio
    async def test_list_documents_success(self, mock_motor_client):
        """Test successful document listing"""
        # Arrange
        documents = [
            {"_id": ObjectId(), "name": "doc1"},
            {"_id": ObjectId(), "name": "doc2"}
        ]
        
        # Create an async iterator mock
        async def async_generator():
            for doc in documents:
                yield doc
        
        mock_cursor = MagicMock()
        mock_cursor.__aiter__ = lambda x: async_generator()
        mock_motor_client["collection"].find.return_value = mock_cursor
        
        # Act
        result = await list_documents("test_collection")
        
        # Assert
        assert result == documents
        mock_motor_client["collection"].find.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_documents_empty(self, mock_motor_client):
        """Test listing documents when collection is empty"""
        # Arrange
        async def empty_generator():
            return
            yield  # unreachable, but makes this a generator
        
        mock_cursor = MagicMock()
        mock_cursor.__aiter__ = lambda x: empty_generator()
        mock_motor_client["collection"].find.return_value = mock_cursor
        
        # Act
        result = await list_documents("test_collection")
        
        # Assert
        assert result == []
        mock_motor_client["collection"].find.assert_called_once()

class TestFindDocumentsByField:
    @pytest.mark.asyncio
    async def test_find_documents_by_field_success(self, mock_motor_client):
        """Test successful document search by field"""
        # Arrange
        field_name = "status"
        field_value = "active"
        matching_documents = [
            {"_id": ObjectId(), "name": "doc1", "status": "active"},
            {"_id": ObjectId(), "name": "doc2", "status": "active"}
        ]
        
        # Create an async iterator mock
        async def async_generator():
            for doc in matching_documents:
                yield doc
        
        mock_cursor = MagicMock()
        mock_cursor.__aiter__ = lambda x: async_generator()
        mock_motor_client["collection"].find.return_value = mock_cursor
        
        # Act
        result = await find_documents_by_field("test_collection", field_name, field_value)
        
        # Assert
        assert result == matching_documents
        mock_motor_client["collection"].find.assert_called_once_with({field_name: field_value})

    @pytest.mark.asyncio
    async def test_find_documents_by_field_no_matches(self, mock_motor_client):
        """Test search with no matching documents"""
        # Arrange
        field_name = "status"
        field_value = "nonexistent"
        
        async def empty_generator():
            return
            yield  # unreachable, but makes this a generator
        
        mock_cursor = MagicMock()
        mock_cursor.__aiter__ = lambda x: empty_generator()
        mock_motor_client["collection"].find.return_value = mock_cursor
        
        # Act
        result = await find_documents_by_field("test_collection", field_name, field_value)
        
        # Assert
        assert result == []
        mock_motor_client["collection"].find.assert_called_once_with({field_name: field_value})

    @pytest.mark.asyncio
    async def test_find_documents_by_field_different_types(self, mock_motor_client):
        """Test search with different field value types"""
        # Arrange - Test with numeric value
        field_name = "count"
        field_value = "5"  # Note: function parameter is str, but we're testing search
        matching_documents = [
            {"_id": ObjectId(), "name": "doc1", "count": "5"}
        ]
        
        async def async_generator():
            for doc in matching_documents:
                yield doc
        
        mock_cursor = MagicMock()
        mock_cursor.__aiter__ = lambda x: async_generator()
        mock_motor_client["collection"].find.return_value = mock_cursor
        
        # Act
        result = await find_documents_by_field("test_collection", field_name, field_value)
        
        # Assert
        assert result == matching_documents
        mock_motor_client["collection"].find.assert_called_once_with({field_name: field_value})

    @pytest.mark.asyncio
    async def test_find_documents_by_field_single_match(self, mock_motor_client):
        """Test search with single matching document"""
        # Arrange
        field_name = "email"
        field_value = "user@example.com"
        matching_document = {"_id": ObjectId(), "name": "John", "email": "user@example.com"}
        
        async def async_generator():
            yield matching_document
        
        mock_cursor = MagicMock()
        mock_cursor.__aiter__ = lambda x: async_generator()
        mock_motor_client["collection"].find.return_value = mock_cursor
        
        # Act
        result = await find_documents_by_field("test_collection", field_name, field_value)
        
        # Assert
        assert result == [matching_document]
        mock_motor_client["collection"].find.assert_called_once_with({field_name: field_value})

    @pytest.mark.asyncio
    async def test_find_documents_by_field_nested_field(self, mock_motor_client):
        """Test search by nested field name"""
        # Arrange
        field_name = "user.role"
        field_value = "admin"
        matching_documents = [
            {"_id": ObjectId(), "user": {"name": "admin1", "role": "admin"}},
        ]
        
        async def async_generator():
            for doc in matching_documents:
                yield doc
        
        mock_cursor = MagicMock()
        mock_cursor.__aiter__ = lambda x: async_generator()
        mock_motor_client["collection"].find.return_value = mock_cursor
        
        # Act
        result = await find_documents_by_field("test_collection", field_name, field_value)
        
        # Assert
        assert result == matching_documents
        mock_motor_client["collection"].find.assert_called_once_with({field_name: field_value})

class TestDeleteDocument:
    @pytest.mark.asyncio
    async def test_delete_document_success(self, mock_motor_client):
        """Test successful document deletion"""
        # Arrange
        doc_id = str(ObjectId())
        mock_result = MagicMock()
        mock_result.deleted_count = 1
        mock_motor_client["collection"].delete_one.return_value = mock_result
        
        # Act
        result = await delete_document("test_collection", doc_id)
        
        # Assert
        assert result is True
        mock_motor_client["collection"].delete_one.assert_awaited_once_with({"_id": ObjectId(doc_id)})

    @pytest.mark.asyncio
    async def test_delete_document_not_found(self, mock_motor_client):
        """Test deleting a non-existent document"""
        # Arrange
        doc_id = str(ObjectId())
        mock_result = MagicMock()
        mock_result.deleted_count = 0
        mock_motor_client["collection"].delete_one.return_value = mock_result
        
        # Act
        result = await delete_document("test_collection", doc_id)
        
        # Assert
        assert result is False
        mock_motor_client["collection"].delete_one.assert_awaited_once_with({"_id": ObjectId(doc_id)})

class TestIntegrationScenarios:
    """Test common database operation workflows"""
    
    @pytest.mark.asyncio
    async def test_crud_workflow(self, mock_motor_client):
        """Test a complete CRUD workflow"""
        collection_name = "test_collection"
        
        # Setup mocks for each operation
        inserted_id = ObjectId()
        doc_id = str(inserted_id)
        document = {"name": "test", "value": 123}
        updated_document = {"name": "updated_test", "value": 456}
        
        # Insert
        insert_result = MagicMock()
        insert_result.inserted_id = inserted_id
        mock_motor_client["collection"].insert_one.return_value = insert_result
        
        # Get
        stored_doc = {"_id": inserted_id, **document}
        mock_motor_client["collection"].find_one.return_value = stored_doc
        
        # Update
        update_result = MagicMock()
        update_result.upserted_id = None
        mock_motor_client["collection"].update_one.return_value = update_result
        
        # Delete
        delete_result = MagicMock()
        delete_result.deleted_count = 1
        mock_motor_client["collection"].delete_one.return_value = delete_result
        
        # Execute CRUD operations
        # Create
        result_id = await insert_document(collection_name, document)
        assert result_id == doc_id
        
        # Read
        retrieved_doc = await get_document(collection_name, doc_id)
        assert retrieved_doc == stored_doc
        
        # Update
        update_id = await update_document(collection_name, doc_id, updated_document)
        assert update_id is None
        
        # Delete
        deleted = await delete_document(collection_name, doc_id)
        assert deleted is True

    @pytest.mark.asyncio
    async def test_crud_with_search_workflow(self, mock_motor_client):
        """Test CRUD workflow including field-based search"""
        collection_name = "test_collection"
        
        # Setup test data
        documents = [
            {"name": "doc1", "status": "active", "category": "type_a"},
            {"name": "doc2", "status": "active", "category": "type_b"},
            {"name": "doc3", "status": "inactive", "category": "type_a"}
        ]
        
        # Mock search by status=active (should return 2 docs)
        active_docs = [doc for doc in documents if doc["status"] == "active"]
        
        async def active_search_generator():
            for doc in active_docs:
                yield {**doc, "_id": ObjectId()}
        
        # Mock search by category=type_a (should return 2 docs)  
        type_a_docs = [doc for doc in documents if doc["category"] == "type_a"]
        
        async def type_a_search_generator():
            for doc in type_a_docs:
                yield {**doc, "_id": ObjectId()}
        
        # Setup different mock cursors for different queries
        def mock_find_side_effect(query):
            mock_cursor = MagicMock()
            if query == {"status": "active"}:
                mock_cursor.__aiter__ = lambda x: active_search_generator()
            elif query == {"category": "type_a"}:
                mock_cursor.__aiter__ = lambda x: type_a_search_generator()
            else:
                async def empty_gen():
                    return
                    yield
                mock_cursor.__aiter__ = lambda x: empty_gen()
            return mock_cursor
        
        mock_motor_client["collection"].find.side_effect = mock_find_side_effect
        
        # Test search operations
        # Search by status
        active_results = await find_documents_by_field(collection_name, "status", "active")
        assert len(active_results) == 2
        
        # Search by category
        type_a_results = await find_documents_by_field(collection_name, "category", "type_a")
        assert len(type_a_results) == 2
        
        # Verify find was called with correct filters
        expected_calls = [
            {"status": "active"},
            {"category": "type_a"}
        ]
        actual_calls = [call[0][0] for call in mock_motor_client["collection"].find.call_args_list]
        assert actual_calls == expected_calls

    @pytest.mark.asyncio 
    async def test_error_handling_chain(self, mock_motor_client):
        """Test error handling across multiple operations"""
        collection_name = "test_collection"
        
        # Test invalid ID error propagation
        with pytest.raises(ValueError, match="Invalid document id format"):
            await get_document(collection_name, "invalid_id")
        
        # Test document not found
        doc_id = str(ObjectId())
        mock_motor_client["collection"].find_one.return_value = None
        
        with pytest.raises(ValueError, match="Document not found"):
            await get_document(collection_name, doc_id) 
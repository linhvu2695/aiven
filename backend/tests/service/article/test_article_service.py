import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime, timezone
from app.services.article.article_service import ArticleService
from app.classes.article import (
    ArticleInfo,
    SearchArticlesResponse,
    CreateOrUpdateArticleRequest,
    CreateOrUpdateArticleResponse,
)


@pytest.fixture
def article_service():
    """Create a fresh instance for each test"""
    # Reset the singleton instance
    ArticleService._instance = None
    return ArticleService()


@pytest.fixture
def mock_article_data():
    return {
        "_id": "test_id_123",
        "title": "Test Article",
        "content": "This is test content",
        "summary": "Test summary",
        "tags": ["test", "article"],
        "parent": "0",
        "created_at": datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
        "updated_at": datetime(2024, 1, 2, 12, 0, 0, tzinfo=timezone.utc),
    }


@pytest.fixture
def create_article_request():
    return CreateOrUpdateArticleRequest(
        title="Test Article",
        content="This is test content",
        summary="Test summary",
        tags=["test", "article"],
        parent="0"
    )


@pytest.fixture
def update_article_request():
    return CreateOrUpdateArticleRequest(
        id="test_id_123",
        title="Updated Article",
        content="This is updated content",
        summary="Updated summary",
        tags=["updated", "article"],
        parent="parent_id_456"
    )


class TestArticleService:
    
    def test_singleton_instance(self):
        """Test that ArticleService is a singleton"""
        service1 = ArticleService()
        service2 = ArticleService()
        assert service1 is service2

    
    @pytest.mark.asyncio
    async def test_get_article_success(self, article_service, mock_article_data):
        """Test successful article retrieval"""
        with patch("app.services.article.article_service.get_document", return_value=mock_article_data):
            article = await article_service.get_article("test_id_123")
            
            assert isinstance(article, ArticleInfo)
            assert article.id == "test_id_123"
            assert article.title == "Test Article"
            assert article.content == "This is test content"
            assert article.summary == "Test summary"
            assert article.tags == ["test", "article"]
            assert article.parent == "0"
            assert article.created_at == datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
            assert article.updated_at == datetime(2024, 1, 2, 12, 0, 0, tzinfo=timezone.utc)


    @pytest.mark.asyncio
    async def test_get_article_nonexistent(self, article_service):
        """Test article retrieval with nonexistent article"""
        with patch("app.services.article.article_service.get_document", return_value=None):
            article = await article_service.get_article("test_id_123")
            assert article is None
        

    @pytest.mark.asyncio
    async def test_get_article_with_missing_fields(self, article_service):
        """Test article retrieval with missing optional fields"""
        minimal_data = {
            "_id": "test_id_123",
        }
        
        with patch("app.services.article.article_service.get_document", return_value=minimal_data):
            article = await article_service.get_article("test_id_123")
            
            assert isinstance(article, ArticleInfo)
            assert article.id == "test_id_123"
            assert article.title == ""
            assert article.content == ""
            assert article.summary == ""
            assert article.tags == []
            assert article.parent == "0"
            assert isinstance(article.created_at, datetime)
            assert isinstance(article.updated_at, datetime)


    @pytest.mark.asyncio
    async def test_search_articles_returns_all_articles(self, article_service):
        """Test search_articles returns all articles"""
        mock_articles = [
            {
                "_id": "1",
                "title": "Article 1",
                "content": "Content 1",
                "summary": "Summary 1",
                "tags": ["tag1"],
                "parent": "0",
                "created_at": datetime(2024, 1, 1, tzinfo=timezone.utc),
                "updated_at": datetime(2024, 1, 1, tzinfo=timezone.utc),
            },
            {
                "_id": "2",
                "title": "Article 2",
                "content": "Content 2",
                "summary": "Summary 2",
                "tags": ["tag2"],
                "parent": "1",
                "created_at": datetime(2024, 1, 2, tzinfo=timezone.utc),
                "updated_at": datetime(2024, 1, 2, tzinfo=timezone.utc),
            },
        ]
        
        with patch("app.services.article.article_service.list_documents", return_value=mock_articles):
            response = await article_service.search_articles()
            
            assert isinstance(response, SearchArticlesResponse)
            assert len(response.articles) == 2
            
            assert response.articles[0].id == "1"
            assert response.articles[0].title == "Article 1"
            assert response.articles[0].content == "Content 1"
            assert response.articles[0].summary == "Summary 1"
            assert response.articles[0].tags == ["tag1"]
            assert response.articles[0].parent == "0"

            assert response.articles[1].id == "2"
            assert response.articles[1].title == "Article 2"
            assert response.articles[1].content == "Content 2"
            assert response.articles[1].summary == "Summary 2"
            assert response.articles[1].tags == ["tag2"]
            assert response.articles[1].parent == "1"


    @pytest.mark.asyncio
    async def test_search_articles_empty_list(self, article_service):
        """Test search_articles with empty database"""
        with patch("app.services.article.article_service.list_documents", return_value=[]):
            response = await article_service.search_articles()
            
            assert isinstance(response, SearchArticlesResponse)
            assert len(response.articles) == 0


    @pytest.mark.asyncio
    async def test_validate_create_article_request_valid(self, article_service, create_article_request):
        """Test validation with valid request"""
        valid, warning = await article_service._validate_create_article_request(create_article_request)
        assert valid is True
        assert warning == ""


    @pytest.mark.asyncio
    async def test_validate_create_article_request_missing_title(self, article_service):
        """Test validation with missing title"""
        request = CreateOrUpdateArticleRequest(
            title="",
            content="Test content",
            summary="Test summary",
            tags=["test"],
            parent="0"
        )
        valid, warning = await article_service._validate_create_article_request(request)
        assert valid is False
        assert "Missing value for field: title" in warning


    @pytest.mark.asyncio
    async def test_validate_create_article_request_missing_content(self, article_service):
        """Test validation with missing content"""
        request = CreateOrUpdateArticleRequest(
            title="Test Title",
            content="",
            summary="Test summary",
            tags=["test"],
            parent="0"
        )
        valid, warning = await article_service._validate_create_article_request(request)
        assert valid is False
        assert "Missing value for field: content" in warning


    @pytest.mark.asyncio
    async def test_validate_create_article_request_none_values(self, article_service):
        """Test validation with None values"""
        # Create a mock request with None title to test validation
        request = MagicMock()
        request.title = None
        request.content = "Test content"
        
        valid, warning = await article_service._validate_create_article_request(request)
        assert valid is False
        assert "Missing value for field: title" in warning


    @pytest.mark.asyncio
    async def test_create_article_success(self, article_service, create_article_request):
        """Test successful article creation"""
        with patch("app.services.article.article_service.insert_document", return_value="new_id_123"):
            response = await article_service.create_or_update_article(create_article_request)
            
            assert isinstance(response, CreateOrUpdateArticleResponse)
            assert response.success is True
            assert response.id == "new_id_123"
            assert response.message == "Article created successfully."


    @pytest.mark.asyncio
    async def test_create_article_validation_failure(self, article_service):
        """Test article creation with validation failure"""
        invalid_request = CreateOrUpdateArticleRequest(
            title="",
            content="Test content",
            summary="Test summary",
            tags=["test"],
            parent="0"
        )
        
        response = await article_service.create_or_update_article(invalid_request)
        
        assert isinstance(response, CreateOrUpdateArticleResponse)
        assert response.success is False
        assert response.id == ""
        assert "Missing value for field: title" in response.message


    @pytest.mark.asyncio
    async def test_create_article_exception(self, article_service, create_article_request):
        """Test article creation with database exception"""
        with patch("app.services.article.article_service.insert_document", side_effect=Exception("Database error")):
            response = await article_service.create_or_update_article(create_article_request)
            
            assert isinstance(response, CreateOrUpdateArticleResponse)
            assert response.success is False
            assert response.id == ""
            assert response.message == "Database error"


    @pytest.mark.asyncio
    async def test_update_article_success(self, article_service, update_article_request):
        """Test successful article update"""
        # Mock parent validation - parent_id_456 should be valid
        with patch("app.services.article.article_service.get_document") as mock_get_doc, \
             patch("app.services.article.article_service.update_document", return_value="test_id_123"):
            
            # Mock parent article exists
            mock_get_doc.return_value = {"_id": "parent_id_456", "title": "Parent Article"}
            
            response = await article_service.create_or_update_article(update_article_request)
            
            assert isinstance(response, CreateOrUpdateArticleResponse)
            assert response.success is True
            assert response.id == "test_id_123"
            assert response.message == "Article updated successfully."


    @pytest.mark.asyncio
    async def test_update_article_invalid_parent(self, article_service, update_article_request):
        """Test article update failure when parent doesn't exist"""
        # Mock parent validation - parent_id_456 does not exist
        with patch("app.services.article.article_service.get_document", return_value=None):
            response = await article_service.create_or_update_article(update_article_request)
            
            assert isinstance(response, CreateOrUpdateArticleResponse)
            assert response.success is False
            assert response.id == ""
            assert "Parent article parent_id_456 does not exist" in response.message


    @pytest.mark.asyncio
    async def test_update_article_exception(self, article_service, update_article_request):
        """Test article update with database exception"""
        # Mock parent validation - parent_id_456 should be valid
        with patch("app.services.article.article_service.get_document") as mock_get_doc, \
             patch("app.services.article.article_service.update_document", side_effect=Exception("Update error")):
            
            # Mock parent article exists
            mock_get_doc.return_value = {"_id": "parent_id_456", "title": "Parent Article"}
            
            response = await article_service.create_or_update_article(update_article_request)
            
            assert isinstance(response, CreateOrUpdateArticleResponse)
            assert response.success is False
            assert response.id == ""
            assert response.message == "Update error"


    @pytest.mark.asyncio
    async def test_delete_article_success(self, article_service):
        """Test successful article deletion"""
        with patch("app.services.article.article_service.delete_document", return_value=True):
            result = await article_service.delete_article("test_id_123")
            
            assert result is True


    @pytest.mark.asyncio
    async def test_delete_article_failure(self, article_service):
        """Test article deletion failure"""
        with patch("app.services.article.article_service.delete_document", return_value=False):
            result = await article_service.delete_article("test_id_123")
            
            assert result is False


    @pytest.mark.asyncio
    async def test_delete_article_exception(self, article_service):
        """Test article deletion with exception"""
        with patch("app.services.article.article_service.delete_document", side_effect=Exception("Delete error")):
            result = await article_service.delete_article("test_id_123")
            
            assert result is False


    @pytest.mark.asyncio
    async def test_delete_article_with_descendants(self, article_service):
        """Test that deleting an article also deletes all its descendants"""
        # Mock data for hierarchical structure:
        # parent_1
        # ├── child_1
        # │   └── grandchild_1
        # └── child_2
        
        mock_child_1 = {"_id": "child_1", "parent": "parent_1"}
        mock_child_2 = {"_id": "child_2", "parent": "parent_1"}
        mock_grandchild_1 = {"_id": "grandchild_1", "parent": "child_1"}
        
        def mock_find_documents_by_field(collection_name, field_name, field_value):
            if field_value == "parent_1":
                return [mock_child_1, mock_child_2]
            elif field_value == "child_1":
                return [mock_grandchild_1]
            elif field_value == "child_2":
                return []
            elif field_value == "grandchild_1":
                return []
            return []
        
        # Track the order of deletion calls
        deletion_calls = []
        
        def mock_delete_document(collection_name, doc_id):
            deletion_calls.append(doc_id)
            return True
        
        with patch("app.services.article.article_service.find_documents_by_field", 
                  side_effect=mock_find_documents_by_field) as mock_find, \
             patch("app.services.article.article_service.delete_document", 
                  side_effect=mock_delete_document) as mock_delete:
            
            result = await article_service.delete_article("parent_1")
            
            # Verify the deletion was successful
            assert result is True
            
            # Verify all documents were deleted in the correct order
            # Should delete descendants first, then parent
            assert "grandchild_1" in deletion_calls
            assert "child_1" in deletion_calls  
            assert "child_2" in deletion_calls
            assert "parent_1" in deletion_calls
            
            # Verify all 4 documents were deleted
            assert len(deletion_calls) == 4
            
            # Verify that grandchild is deleted before its parent (child_1)
            grandchild_index = deletion_calls.index("grandchild_1")
            child1_index = deletion_calls.index("child_1")
            assert grandchild_index < child1_index
            
            # Verify that children are deleted before their parent (parent_1)
            parent_index = deletion_calls.index("parent_1")
            assert child1_index < parent_index
            assert deletion_calls.index("child_2") < parent_index
            
            # Verify find_documents_by_field was called for each article to find its children
            assert mock_find.call_count == 4  # parent_1, child_1, child_2, grandchild_1


    @pytest.mark.asyncio
    async def test_delete_article_with_descendants_child_deletion_failure(self, article_service):
        """Test that parent deletion fails if any child deletion fails"""
        mock_child_1 = {"_id": "child_1", "parent": "parent_1"}
        mock_child_2 = {"_id": "child_2", "parent": "parent_1"}
        
        def mock_find_documents_by_field(collection_name, field_name, field_value):
            if field_value == "parent_1":
                return [mock_child_1, mock_child_2]
            return []
        
        deletion_calls = []
        
        def mock_delete_document(collection_name, doc_id):
            deletion_calls.append(doc_id)
            # Simulate failure when deleting child_2
            if doc_id == "child_2":
                return False
            return True
        
        with patch("app.services.article.article_service.find_documents_by_field", 
                  side_effect=mock_find_documents_by_field), \
             patch("app.services.article.article_service.delete_document", 
                  side_effect=mock_delete_document):
            
            result = await article_service.delete_article("parent_1")
            
            # Verify the deletion failed
            assert result is False
            
            # Verify that child_1 was deleted but child_2 failed, and parent_1 was not attempted
            assert "child_1" in deletion_calls
            assert "child_2" in deletion_calls
            assert "parent_1" not in deletion_calls  # Should not reach parent deletion
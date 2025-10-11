import pytest
from httpx import AsyncClient, ASGITransport
from fastapi import FastAPI
from unittest.mock import patch, AsyncMock
from datetime import datetime, timezone
from app.api.article import router
from app.classes.article import (
    SearchArticlesResponse,
    ArticleInfo,
    CreateOrUpdateArticleRequest,
    CreateOrUpdateArticleResponse,
    DeleteArticleResponse,
)

# Test constants for MongoDB ObjectIds
TEST_ARTICLE_ID = "000000000000000000000001"

app = FastAPI()
app.include_router(router, prefix="/articles")


@pytest.mark.asyncio
async def test_get_article_api():
    """Test GET /articles/id={id} endpoint"""
    mock_article = ArticleInfo(
        id="test_id_123",
        title="Test Article",
        content="This is test content",
        summary="Test summary",
        tags=["test", "article"],
        parent="0",
        created_at=datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
        updated_at=datetime(2024, 1, 2, 12, 0, 0, tzinfo=timezone.utc),
    )
    
    with patch("app.services.article.article_service.ArticleService.get_article", new=AsyncMock(return_value=mock_article)):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.get("/articles/id=test_id_123")
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == "test_id_123"
            assert data["title"] == "Test Article"
            assert data["content"] == "This is test content"
            assert data["summary"] == "Test summary"
            assert data["tags"] == ["test", "article"]
            assert data["parent"] == "0"


@pytest.mark.asyncio
async def test_search_articles_api():
    """Test GET /articles/search endpoint"""
    mock_response = SearchArticlesResponse(articles=[
        ArticleInfo(
            id="1",
            title="Article 1",
            content="Content 1",
            summary="Summary 1",
            tags=["tag1"],
            parent="0",
            created_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
            updated_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
        ),
        ArticleInfo(
            id="2",
            title="Article 2",
            content="Content 2",
            summary="Summary 2",
            tags=["tag2"],
            parent="1",
            created_at=datetime(2024, 1, 2, tzinfo=timezone.utc),
            updated_at=datetime(2024, 1, 2, tzinfo=timezone.utc),
        ),
    ])
    
    with patch("app.services.article.article_service.ArticleService.search_articles", new=AsyncMock(return_value=mock_response)):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.get("/articles/search")
            assert response.status_code == 200
            data = response.json()
            assert "articles" in data
            assert len(data["articles"]) == 2
            
            assert data["articles"][0]["id"] == "1"
            assert data["articles"][0]["title"] == "Article 1"
            assert data["articles"][0]["content"] == "Content 1"
            assert data["articles"][0]["summary"] == "Summary 1"
            assert data["articles"][0]["tags"] == ["tag1"]
            assert data["articles"][0]["parent"] == "0"
            
            assert data["articles"][1]["id"] == "2"
            assert data["articles"][1]["title"] == "Article 2"
            assert data["articles"][1]["content"] == "Content 2"
            assert data["articles"][1]["summary"] == "Summary 2"
            assert data["articles"][1]["tags"] == ["tag2"]
            assert data["articles"][1]["parent"] == "1"


@pytest.mark.asyncio
async def test_search_articles_api_empty():
    """Test GET /articles/search endpoint with empty results"""
    mock_response = SearchArticlesResponse(articles=[])
    
    with patch("app.services.article.article_service.ArticleService.search_articles", new=AsyncMock(return_value=mock_response)):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.get("/articles/search")
            assert response.status_code == 200
            data = response.json()
            assert "articles" in data
            assert len(data["articles"]) == 0


@pytest.mark.asyncio
async def test_create_article_api():
    """Test POST /articles/ endpoint for creating a new article"""
    request_data = {
        "title": "New Article",
        "content": "This is new content",
        "summary": "New summary",
        "tags": ["new", "article"],
        "parent": "0"
    }
    
    mock_response = CreateOrUpdateArticleResponse(
        success=True,
        id="new_article_id",
        message="Article created successfully."
    )
    
    with patch("app.services.article.article_service.ArticleService.create_or_update_article", new=AsyncMock(return_value=mock_response)):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.post("/articles/", json=request_data)
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["id"] == "new_article_id"
            assert data["message"] == "Article created successfully."


@pytest.mark.asyncio
async def test_update_article_api():
    """Test POST /articles/ endpoint for updating an existing article"""
    request_data = {
        "id": "existing_id",
        "title": "Updated Article",
        "content": "This is updated content",
        "summary": "Updated summary",
        "tags": ["updated", "article"],
        "parent": "parent_id"
    }
    
    mock_response = CreateOrUpdateArticleResponse(
        success=True,
        id="existing_id",
        message="Article updated successfully."
    )
    
    with patch("app.services.article.article_service.ArticleService.create_or_update_article", new=AsyncMock(return_value=mock_response)):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.post("/articles/", json=request_data)
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["id"] == "existing_id"
            assert data["message"] == "Article updated successfully."


@pytest.mark.asyncio
async def test_create_article_api_failure():
    """Test POST /articles/ endpoint with validation failure"""
    request_data = {
        "title": "",  # Invalid empty title
        "content": "Test content",
        "summary": "Test summary",
        "tags": ["test"],
        "parent": "0"
    }
    
    mock_response = CreateOrUpdateArticleResponse(
        success=False,
        id="",
        message="Invalid article info. Missing value for field: title"
    )
    
    with patch("app.services.article.article_service.ArticleService.create_or_update_article", new=AsyncMock(return_value=mock_response)):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.post("/articles/", json=request_data)
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is False
            assert data["id"] == ""
            assert "Missing value for field: title" in data["message"]


@pytest.mark.asyncio
async def test_create_article_api_with_minimal_data():
    """Test POST /articles/ endpoint with minimal required data"""
    request_data = {
        "title": "Minimal Article",
        "content": "Minimal content",
        "summary": "",
        "tags": [],
        # parent defaults to "0"
    }
    
    mock_response = CreateOrUpdateArticleResponse(
        success=True,
        id="minimal_article_id",
        message="Article created successfully."
    )
    
    with patch("app.services.article.article_service.ArticleService.create_or_update_article", new=AsyncMock(return_value=mock_response)):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.post("/articles/", json=request_data)
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["id"] == "minimal_article_id"
            assert data["message"] == "Article created successfully."


@pytest.mark.asyncio
async def test_delete_article_api_success():
    """Test DELETE /articles/{id} endpoint with successful deletion"""
    mock_response = DeleteArticleResponse(success=True, message="")
    
    with patch("app.services.article.article_service.ArticleService.delete_article", new=AsyncMock(return_value=mock_response)):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.delete(f"/articles/{TEST_ARTICLE_ID}")
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["message"] == ""


@pytest.mark.asyncio
async def test_delete_article_api_failure():
    """Test DELETE /articles/{id} endpoint with deletion failure"""
    mock_response = DeleteArticleResponse(success=False, message="Failed to delete article 000000000000000000000001")
    
    with patch("app.services.article.article_service.ArticleService.delete_article", new=AsyncMock(return_value=mock_response)):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.delete(f"/articles/{TEST_ARTICLE_ID}")
            assert response.status_code == 400
            data = response.json()
            assert data["detail"] == "Failed to delete article 000000000000000000000001"


@pytest.mark.asyncio
async def test_delete_article_api_invalid_id():
    """Test DELETE /articles/{id} endpoint with invalid ObjectId"""
    mock_response = DeleteArticleResponse(success=False, message="Invalid article ID")
    
    with patch("app.services.article.article_service.ArticleService.delete_article", new=AsyncMock(return_value=mock_response)):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.delete("/articles/invalid-id")
            assert response.status_code == 400
            data = response.json()
            assert data["detail"] == "Invalid article ID"


@pytest.mark.asyncio
async def test_api_error_handling():
    """Test API error handling when service raises exceptions"""
    with patch("app.services.article.article_service.ArticleService.get_article", new=AsyncMock(side_effect=Exception("Database error"))):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            # The API doesn't have explicit error handling, so the exception will propagate
            try:
                response = await ac.get("/articles/id=test_id")
                # If we get here, the exception was handled by FastAPI internally
                assert response.status_code == 500
            except Exception as e:
                # If the exception propagates, that's also expected behavior
                assert "Database error" in str(e) 
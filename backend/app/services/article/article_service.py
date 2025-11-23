import logging
from datetime import datetime, timezone

from bson.objectid import ObjectId
from app.classes.article import (
    CreateOrUpdateArticleRequest,
    CreateOrUpdateArticleResponse,
    ArticleInfo,
    DeleteArticleResponse,
    SearchArticlesResponse,
)
from app.core.database import delete_document, find_documents_by_field, MongoDB

ARTICLE_COLLECTION_NAME = "articles"


class ArticleService:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance") or cls._instance is None:
            cls._instance = super(ArticleService, cls).__new__(cls)
        return cls._instance

    async def _validate_create_article_request(
        self, request: CreateOrUpdateArticleRequest
    ) -> tuple[bool, str]:
        warning = ""

        # Required fields
        required_fields = ["title", "content"]
        for field in required_fields:
            value = getattr(request, field, None)
            if value is None or (isinstance(value, str) and value.strip() == ""):
                warning = f"Invalid article info. Missing value for field: {field}"
                return False, warning
            
        # Check if parent is a valid article id
        if request.parent is None or request.parent == "":
            request.parent = "0"
        elif request.parent != "0":
            parent_article = await self.get_article(request.parent)
            if not parent_article:
                warning = f"Invalid article info. Parent article {request.parent} does not exist"
                return False, warning

        return True, warning
    
    async def get_article(self, id: str) -> ArticleInfo | None:
        data = await MongoDB().get_document(ARTICLE_COLLECTION_NAME, id)
        if not data:
            return None

        return ArticleInfo(
            id=str(data.get("_id", "")),
            title=data.get("title", ""),
            content=data.get("content", ""),
            summary=data.get("summary", ""),
            tags=data.get("tags", []),
            parent=data.get("parent", "0"),
            created_at=data.get("created_at", datetime.now(timezone.utc)),
            updated_at=data.get("updated_at", datetime.now(timezone.utc)),
        )

    async def create_or_update_article(
        self, request: CreateOrUpdateArticleRequest
    ) -> CreateOrUpdateArticleResponse:
        valid, warning = await self._validate_create_article_request(request)
        if not valid:
            logging.getLogger("uvicorn.warning").warning(warning)
            return CreateOrUpdateArticleResponse(success=False, id="", message=warning)

        try:
            current_time = datetime.now(timezone.utc).isoformat()
            document = {
                "title": request.title,
                "content": request.content,
                "summary": request.summary,
                "tags": request.tags,
                "parent": request.parent,
                "updated_at": current_time,
            }
            
            if getattr(request, "id", None):  # Update if id is present
                await MongoDB().update_document(
                    ARTICLE_COLLECTION_NAME, str(request.id), document
                )

                return CreateOrUpdateArticleResponse(
                    success=True,
                    id=str(request.id),
                    message="Article updated successfully.",
                )
            else:  # Insert new
                document["created_at"] = current_time
                inserted_id = await MongoDB().insert_document(ARTICLE_COLLECTION_NAME, document)
                return CreateOrUpdateArticleResponse(
                    success=True, id=inserted_id, message="Article created successfully."
                )
        except Exception as e:
            return CreateOrUpdateArticleResponse(success=False, id="", message=str(e))

    async def search_articles(self) -> SearchArticlesResponse:
        documents = await MongoDB().list_documents(ARTICLE_COLLECTION_NAME)
        articles = [
            ArticleInfo(
                id=str(doc.get("_id", "")),
                title=doc.get("title", ""),
                content=doc.get("content", ""),
                summary=doc.get("summary", ""),
                tags=doc.get("tags", []),
                parent=doc.get("parent", "0"),
                created_at=doc.get("created_at", datetime.now(timezone.utc)),
                updated_at=doc.get("updated_at", datetime.now(timezone.utc)),
            )
            for doc in documents
        ]
        return SearchArticlesResponse(articles=articles)
    
    async def delete_article(self, id: str) -> DeleteArticleResponse:        
        if not ObjectId.is_valid(id):
            return DeleteArticleResponse(success=False, message="Invalid article ID")
        
        try:
            # First, find all children of this article
            child_documents = await find_documents_by_field(ARTICLE_COLLECTION_NAME, "parent", id)
            
            # Recursively delete all children
            for child_doc in child_documents:
                child_id = str(child_doc.get("_id", ""))
                if child_id:
                    child_deleted = await self.delete_article(child_id)
                    if not child_deleted.success:
                        return DeleteArticleResponse(success=False, message=f"Failed to delete child article {child_id}")
            
            # After all children are deleted, delete the original article
            article_deleted = await delete_document(ARTICLE_COLLECTION_NAME, id)
            if article_deleted:
                return DeleteArticleResponse(success=True, message="")
            else:
                return DeleteArticleResponse(success=False, message=f"Failed to delete article {id}")
        except Exception as e:
            return DeleteArticleResponse(success=False, message=str(e))
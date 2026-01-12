from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class ArticleInfo(BaseModel):
    id: str
    title: str
    content: str
    summary: str
    tags: list[str]
    parent: str  # Parent article ID, "0" for root level
    created_at: datetime
    updated_at: datetime
    added_to_graph: bool = False

class CreateOrUpdateArticleRequest(BaseModel):
    id: Optional[str] = None
    title: str
    content: str
    summary: str
    tags: list[str]
    parent: str = "0"  # Default to root level

class CreateOrUpdateArticleResponse(BaseModel):
    success: bool
    id: str
    message: str

class SearchArticlesResponse(BaseModel):
    articles: list[ArticleInfo] 

class DeleteArticleResponse(BaseModel):
    success: bool
    message: str

class AddArticleToGraphRequest(BaseModel):
    article_id: str
    force_readd: bool = False

class AddArticleToGraphResponse(BaseModel):
    success: bool
    message: str
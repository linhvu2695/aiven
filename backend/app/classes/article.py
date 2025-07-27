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
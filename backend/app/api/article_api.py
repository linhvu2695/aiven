from fastapi import APIRouter, HTTPException
from app.classes.article import CreateOrUpdateArticleRequest, CreateOrUpdateArticleResponse, DeleteArticleResponse, SearchArticlesResponse
from app.services.article.article_service import ArticleService

router = APIRouter()

@router.get("/id={id}")
async def get_article(id: str):
    return await ArticleService().get_article(id)

@router.post("/", response_model=CreateOrUpdateArticleResponse)
async def create_or_update_article(request: CreateOrUpdateArticleRequest):
    return await ArticleService().create_or_update_article(request)

@router.get("/search", response_model=SearchArticlesResponse)
async def search_articles():
    return await ArticleService().search_articles()

@router.delete("/{id}", response_model=DeleteArticleResponse)
async def delete_article(id: str):
    response = await ArticleService().delete_article(id)

    if response.success:
        return response
    else:
        raise HTTPException(status_code=400, detail=response.message) 
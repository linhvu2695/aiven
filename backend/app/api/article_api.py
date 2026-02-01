from typing import Optional
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from app.classes.article import (
    AddArticleToGraphRequest,
    AddArticleToGraphResponse,
    CreateOrUpdateArticleRequest,
    CreateOrUpdateArticleResponse,
    DeleteArticleResponse,
    ParsePDFToArticleRequest,
    ParsePDFToArticleResponse,
    SearchArticlesResponse,
)
from app.services.article.article_service import ArticleService
from app.services.article.pdf_parser_service import PDFParserService

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

@router.post("/addgraph", response_model=AddArticleToGraphResponse)
async def add_article_to_graph(request: AddArticleToGraphRequest):
    response = await ArticleService().add_article_to_graph(request)

    if response.success:
        return response
    else:
        raise HTTPException(status_code=400, detail=response.message)


@router.post("/from-pdf", response_model=ParsePDFToArticleResponse)
async def parse_pdf_to_article(
    file: UploadFile = File(...),
    title: str = Form(""),
    summary: str = Form(""),
    parent: str = Form("0"),
):
    """
    Upload a PDF file and convert it to a markdown article.
    
    - file: PDF file to parse
    - title: Optional title override (otherwise extracted from PDF)
    - summary: Article summary
    - parent: Parent article ID ("0" for root level)
    """
    # Validate file type
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    # Read file content
    file_content = await file.read()

    # Create request DTO
    request = ParsePDFToArticleRequest(
        file_content=file_content,
        filename=file.filename,
        title=title,
        summary=summary,
        parent=parent,
    )

    response = await PDFParserService().parse_pdf_to_article(request)

    if response.success:
        return response
    else:
        raise HTTPException(status_code=400, detail=response.message)
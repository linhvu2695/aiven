import logging
import re
import tempfile
import os
from pathlib import Path

from llama_cloud import AsyncLlamaCloud

from app.classes.article import (
    CreateOrUpdateArticleRequest,
    ParsePDFToArticleRequest,
    ParsePDFToArticleResponse,
)
from app.utils.string.string_utils import is_empty_string
from app.core.config import settings
from app.services.article.article_service import ArticleService

UNTITLED_ARTICLE = "Untitled Article"

class PDFParserService:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance") or cls._instance is None:
            cls._instance = super(PDFParserService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self.client = AsyncLlamaCloud(api_key=settings.llamacloud_api_key)
        self.logger = logging.getLogger("uvicorn.info")

    def _extract_title_from_markdown(self, markdown: str) -> str:
        """
        Extract title from the first H1 heading in markdown content.
        Falls back to first line if no H1 found.
        """
        # Look for first H1 heading
        h1_match = re.search(r"^#\s+(.+)$", markdown, re.MULTILINE)
        if h1_match:
            return h1_match.group(1).strip()

        # Fallback: use first non-empty line
        lines = markdown.strip().split("\n")
        for line in lines:
            stripped = line.strip()
            if stripped:
                # Remove any markdown formatting
                cleaned = re.sub(r"^#+\s*", "", stripped)
                return cleaned[:100]  # Limit title length

        return "Untitled Document"

    async def parse_pdf_to_article(
        self,
        request: ParsePDFToArticleRequest,
    ) -> ParsePDFToArticleResponse:
        """
        Parse a PDF file and create an article from its markdown content.
        
        Args:
            request: Request containing file content, filename, and article options
            
        Returns:
            ParsePDFToArticleResponse with the created article info
        """
        temp_file_path = None
        
        try:
            # Save to temporary file
            self.logger.info(f"Step 1: Saving PDF to temporary file: {request.filename}")
            with tempfile.NamedTemporaryFile(
                suffix=".pdf", delete=False
            ) as temp_file:
                temp_file.write(request.file_content)
                temp_file_path = temp_file.name

            # Upload file to LlamaCloud
            self.logger.info(f"Step 2: Uploading PDF to LlamaCloud: {request.filename}")
            file_obj = await self.client.files.create(
                file=temp_file_path,
                purpose="parse"
            )
            self.logger.info(f"Step 2: File uploaded with ID: {file_obj.id}")

            # Parse the document with agentic tier for high quality
            self.logger.info(f"Step 3: Parsing PDF: {request.filename}")
            result = await self.client.parsing.parse(
                file_id=file_obj.id,
                tier="agentic",
                version="latest",
                expand=["markdown"],
            )

            # Extract markdown content from all pages
            markdown_pages = []
            if result.markdown and result.markdown.pages:
                for page in result.markdown.pages:
                    # Use getattr to safely access markdown (some pages may fail)
                    page_markdown = getattr(page, "markdown", None)
                    if page_markdown:
                        markdown_pages.append(page_markdown)

            if not markdown_pages:
                return ParsePDFToArticleResponse(
                    success=False,
                    article_id="",
                    title="",
                    message="Failed to extract markdown content from PDF",
                )

            full_markdown = "\n\n".join(markdown_pages)

            # Determine title
            self.logger.info(f"Step 4: Determining title from PDF: {request.filename}")
            title = request.title
            if is_empty_string(title):
                title = self._extract_title_from_markdown(full_markdown)
                if not title:
                    # Use filename without extension as fallback
                    title = Path(request.filename).stem
            self.logger.info(f"Step 4: Title determined from PDF: {title}")

            # Create article
            self.logger.info(f"Step 5: Creating article from PDF: {title}")
            article_response = await ArticleService().create_or_update_article(
                CreateOrUpdateArticleRequest(
                    title=title or UNTITLED_ARTICLE, 
                    content=full_markdown, 
                    summary=request.summary, 
                    tags=[], 
                    parent=request.parent)
                    )

            if not article_response.success:
                return ParsePDFToArticleResponse(
                    success=False,
                    article_id="",
                    title="",
                    message=f"Failed to create article: {article_response.message}",
                )

            return ParsePDFToArticleResponse(
                success=True,
                article_id=article_response.id,
                title=title or UNTITLED_ARTICLE,
                message="PDF parsed and article created successfully",
            )

        except Exception as e:
            self.logger.error(f"Error parsing PDF: {str(e)}")
            return ParsePDFToArticleResponse(
                success=False,
                article_id="",
                title="",
                message=f"Error parsing PDF: {str(e)}",
            )

        finally:
            # Clean up temporary file
            self.logger.info(f"Step 6: Cleaning up temporary file: {temp_file_path}")
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.unlink(temp_file_path)
                except Exception as e:
                    self.logger.warning(f"Step 6: Failed to delete temp file: {e}")

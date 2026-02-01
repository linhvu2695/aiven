import pytest
from unittest.mock import patch, MagicMock, AsyncMock

from app.services.article.pdf_parser_service import PDFParserService, UNTITLED_ARTICLE
from app.classes.article import (
    ParsePDFToArticleRequest,
    ParsePDFToArticleResponse,
    CreateOrUpdateArticleResponse,
)


# Test constants
TEST_PDF_CONTENT = b"%PDF-1.4 fake pdf content"
TEST_FILENAME = "test_document.pdf"
TEST_ARTICLE_ID = "507f1f77bcf86cd799439011"


@pytest.fixture
def pdf_parser_service():
    """Create a fresh instance for each test"""
    # Reset the singleton instance
    PDFParserService._instance = None
    
    with patch("app.services.article.pdf_parser_service.AsyncLlamaCloud"):
        service = PDFParserService()
        return service


@pytest.fixture
def parse_pdf_request():
    """Create a basic PDF parse request"""
    return ParsePDFToArticleRequest(
        file_content=TEST_PDF_CONTENT,
        filename=TEST_FILENAME,
        title=None,
        summary="Test summary",
        parent="0",
    )


@pytest.fixture
def parse_pdf_request_with_title():
    """Create a PDF parse request with explicit title"""
    return ParsePDFToArticleRequest(
        file_content=TEST_PDF_CONTENT,
        filename=TEST_FILENAME,
        title="Custom Title",
        summary="Test summary",
        parent="0",
    )


class TestExtractTitleFromMarkdown:
    """Tests for the _extract_title_from_markdown method"""

    def test_extract_title_from_h1_heading(self, pdf_parser_service: PDFParserService):
        """Test extraction of title from H1 heading"""
        markdown = """Some intro text

# Main Title

Content goes here
"""
        title = pdf_parser_service._extract_title_from_markdown(markdown)
        assert title == "Main Title"

    def test_extract_title_from_h1_at_start(self, pdf_parser_service: PDFParserService):
        """Test extraction when H1 is at the start"""
        markdown = """# Document Title

Some content here
"""
        title = pdf_parser_service._extract_title_from_markdown(markdown)
        assert title == "Document Title"

    def test_extract_title_strips_whitespace(self, pdf_parser_service: PDFParserService):
        """Test that extracted title is stripped of whitespace"""
        markdown = "#   Title with spaces   \n\nContent"
        title = pdf_parser_service._extract_title_from_markdown(markdown)
        assert title == "Title with spaces"

    def test_fallback_to_first_line_when_no_h1(self, pdf_parser_service: PDFParserService):
        """Test fallback to first non-empty line when no H1 found"""
        markdown = """First Line Title

Some content without H1 heading
"""
        title = pdf_parser_service._extract_title_from_markdown(markdown)
        assert title == "First Line Title"

    def test_fallback_removes_other_heading_markers(self, pdf_parser_service: PDFParserService):
        """Test that fallback removes ## or ### markers from first line"""
        markdown = """## Second Level Title

Content here
"""
        title = pdf_parser_service._extract_title_from_markdown(markdown)
        assert title == "Second Level Title"

    def test_fallback_with_bold_text(self, pdf_parser_service: PDFParserService):
        """Test fallback with markdown formatting in first line"""
        markdown = """**Bold Title**

Content
"""
        title = pdf_parser_service._extract_title_from_markdown(markdown)
        assert title == "**Bold Title**"

    def test_returns_untitled_for_empty_markdown(self, pdf_parser_service: PDFParserService):
        """Test returns 'Untitled Document' for empty markdown"""
        title = pdf_parser_service._extract_title_from_markdown("")
        assert title == "Untitled Document"

    def test_returns_untitled_for_whitespace_only(self, pdf_parser_service: PDFParserService):
        """Test returns 'Untitled Document' for whitespace-only markdown"""
        title = pdf_parser_service._extract_title_from_markdown("   \n\n   \t  ")
        assert title == "Untitled Document"

    def test_title_truncated_to_100_chars(self, pdf_parser_service: PDFParserService):
        """Test that fallback title is truncated to 100 characters"""
        long_title = "A" * 150
        markdown = f"{long_title}\n\nContent"
        title = pdf_parser_service._extract_title_from_markdown(markdown)
        assert len(title) == 100
        assert title == "A" * 100

    def test_h1_takes_priority_over_earlier_text(self, pdf_parser_service: PDFParserService):
        """Test that H1 heading takes priority even with earlier text"""
        markdown = """orange**logic**

# Groups
Last updated 08/27/2025

Set up and use Groups
"""
        title = pdf_parser_service._extract_title_from_markdown(markdown)
        assert title == "Groups"

    def test_skips_empty_lines_in_fallback(self, pdf_parser_service: PDFParserService):
        """Test that empty lines are skipped when falling back"""
        markdown = """


   

Actual First Line

Content
"""
        title = pdf_parser_service._extract_title_from_markdown(markdown)
        assert title == "Actual First Line"


class TestParsePDFToArticle:
    """Tests for the parse_pdf_to_article method"""

    def test_singleton_instance(self):
        """Test that PDFParserService is a singleton"""
        PDFParserService._instance = None
        
        with patch("app.services.article.pdf_parser_service.AsyncLlamaCloud"):
            service1 = PDFParserService()
            service2 = PDFParserService()
            assert service1 is service2

    @pytest.mark.asyncio
    async def test_successful_parse_with_title_from_markdown(
        self, pdf_parser_service: PDFParserService, parse_pdf_request: ParsePDFToArticleRequest
    ):
        """Test successful PDF parsing with title extracted from markdown"""
        # Mock LlamaCloud file upload
        mock_file_obj = MagicMock()
        mock_file_obj.id = "file-123"
        pdf_parser_service.client.files.create = AsyncMock(return_value=mock_file_obj)
        
        # Mock LlamaCloud parsing result
        mock_page = MagicMock()
        mock_page.markdown = "# Document Title\n\nContent here"
        mock_result = MagicMock()
        mock_result.markdown = MagicMock()
        mock_result.markdown.pages = [mock_page]
        pdf_parser_service.client.parsing.parse = AsyncMock(return_value=mock_result)
        
        # Mock ArticleService
        with patch("app.services.article.pdf_parser_service.ArticleService") as mock_article_service_class:
            mock_article_service = MagicMock()
            mock_article_service_class.return_value = mock_article_service
            mock_article_service.create_or_update_article = AsyncMock(
                return_value=CreateOrUpdateArticleResponse(
                    success=True,
                    id=TEST_ARTICLE_ID,
                    message="Article created successfully."
                )
            )
            
            response = await pdf_parser_service.parse_pdf_to_article(parse_pdf_request)
            
            assert isinstance(response, ParsePDFToArticleResponse)
            assert response.success is True
            assert response.article_id == TEST_ARTICLE_ID
            assert response.title == "Document Title"
            assert "successfully" in response.message

    @pytest.mark.asyncio
    async def test_successful_parse_with_custom_title(
        self, pdf_parser_service: PDFParserService, parse_pdf_request_with_title: ParsePDFToArticleRequest
    ):
        """Test PDF parsing uses custom title from request"""
        mock_file_obj = MagicMock()
        mock_file_obj.id = "file-123"
        pdf_parser_service.client.files.create = AsyncMock(return_value=mock_file_obj)
        
        mock_page = MagicMock()
        mock_page.markdown = "# Different Title\n\nContent"
        mock_result = MagicMock()
        mock_result.markdown = MagicMock()
        mock_result.markdown.pages = [mock_page]
        pdf_parser_service.client.parsing.parse = AsyncMock(return_value=mock_result)
        
        with patch("app.services.article.pdf_parser_service.ArticleService") as mock_article_service_class:
            mock_article_service = MagicMock()
            mock_article_service_class.return_value = mock_article_service
            mock_article_service.create_or_update_article = AsyncMock(
                return_value=CreateOrUpdateArticleResponse(
                    success=True,
                    id=TEST_ARTICLE_ID,
                    message="Article created successfully."
                )
            )
            
            response = await pdf_parser_service.parse_pdf_to_article(parse_pdf_request_with_title)
            
            assert response.success is True
            assert response.title == "Custom Title"

    @pytest.mark.asyncio
    async def test_title_fallback_to_untitled_document(
        self, pdf_parser_service: PDFParserService, parse_pdf_request: ParsePDFToArticleRequest
    ):
        """Test title falls back to 'Untitled Document' when markdown has no extractable title"""
        mock_file_obj = MagicMock()
        mock_file_obj.id = "file-123"
        pdf_parser_service.client.files.create = AsyncMock(return_value=mock_file_obj)
        
        # Markdown with no title and empty content
        mock_page = MagicMock()
        mock_page.markdown = "   \n\n   "  # Only whitespace
        mock_result = MagicMock()
        mock_result.markdown = MagicMock()
        mock_result.markdown.pages = [mock_page]
        pdf_parser_service.client.parsing.parse = AsyncMock(return_value=mock_result)
        
        with patch("app.services.article.pdf_parser_service.ArticleService") as mock_article_service_class:
            mock_article_service = MagicMock()
            mock_article_service_class.return_value = mock_article_service
            mock_article_service.create_or_update_article = AsyncMock(
                return_value=CreateOrUpdateArticleResponse(
                    success=True,
                    id=TEST_ARTICLE_ID,
                    message="Article created successfully."
                )
            )
            
            # Mock is_empty_string to work correctly
            with patch("app.services.article.pdf_parser_service.is_empty_string", return_value=True):
                response = await pdf_parser_service.parse_pdf_to_article(parse_pdf_request)
            
            assert response.success is True
            # Title should fall back to "Untitled Document" from _extract_title_from_markdown
            assert response.title == "Untitled Document"

    @pytest.mark.asyncio
    async def test_multiple_pages_combined(
        self, pdf_parser_service: PDFParserService, parse_pdf_request: ParsePDFToArticleRequest
    ):
        """Test that markdown from multiple pages is combined"""
        mock_file_obj = MagicMock()
        mock_file_obj.id = "file-123"
        pdf_parser_service.client.files.create = AsyncMock(return_value=mock_file_obj)
        
        # Multiple pages
        mock_page1 = MagicMock()
        mock_page1.markdown = "# Page 1\n\nContent of page 1"
        mock_page2 = MagicMock()
        mock_page2.markdown = "## Page 2\n\nContent of page 2"
        mock_result = MagicMock()
        mock_result.markdown = MagicMock()
        mock_result.markdown.pages = [mock_page1, mock_page2]
        pdf_parser_service.client.parsing.parse = AsyncMock(return_value=mock_result)
        
        with patch("app.services.article.pdf_parser_service.ArticleService") as mock_article_service_class:
            mock_article_service = MagicMock()
            mock_article_service_class.return_value = mock_article_service
            mock_article_service.create_or_update_article = AsyncMock(
                return_value=CreateOrUpdateArticleResponse(
                    success=True,
                    id=TEST_ARTICLE_ID,
                    message="Article created successfully."
                )
            )
            
            response = await pdf_parser_service.parse_pdf_to_article(parse_pdf_request)
            
            # Verify the content passed to ArticleService contains both pages
            call_args = mock_article_service.create_or_update_article.call_args
            article_request = call_args[0][0]
            assert "Page 1" in article_request.content
            assert "Page 2" in article_request.content

    @pytest.mark.asyncio
    async def test_failed_markdown_extraction(
        self, pdf_parser_service: PDFParserService, parse_pdf_request: ParsePDFToArticleRequest
    ):
        """Test failure when no markdown content is extracted"""
        mock_file_obj = MagicMock()
        mock_file_obj.id = "file-123"
        pdf_parser_service.client.files.create = AsyncMock(return_value=mock_file_obj)
        
        # Empty pages
        mock_result = MagicMock()
        mock_result.markdown = MagicMock()
        mock_result.markdown.pages = []
        pdf_parser_service.client.parsing.parse = AsyncMock(return_value=mock_result)
        
        response = await pdf_parser_service.parse_pdf_to_article(parse_pdf_request)
        
        assert response.success is False
        assert response.article_id == ""
        assert response.title == ""
        assert "Failed to extract markdown" in response.message

    @pytest.mark.asyncio
    async def test_failed_markdown_extraction_no_markdown_attr(
        self, pdf_parser_service: PDFParserService, parse_pdf_request: ParsePDFToArticleRequest
    ):
        """Test failure when result has no markdown attribute"""
        mock_file_obj = MagicMock()
        mock_file_obj.id = "file-123"
        pdf_parser_service.client.files.create = AsyncMock(return_value=mock_file_obj)
        
        # No markdown attribute
        mock_result = MagicMock()
        mock_result.markdown = None
        pdf_parser_service.client.parsing.parse = AsyncMock(return_value=mock_result)
        
        response = await pdf_parser_service.parse_pdf_to_article(parse_pdf_request)
        
        assert response.success is False
        assert "Failed to extract markdown" in response.message

    @pytest.mark.asyncio
    async def test_llamacloud_upload_error(
        self, pdf_parser_service: PDFParserService, parse_pdf_request: ParsePDFToArticleRequest
    ):
        """Test handling of LlamaCloud file upload error"""
        pdf_parser_service.client.files.create = AsyncMock(
            side_effect=Exception("LlamaCloud upload failed")
        )
        
        response = await pdf_parser_service.parse_pdf_to_article(parse_pdf_request)
        
        assert response.success is False
        assert "LlamaCloud upload failed" in response.message

    @pytest.mark.asyncio
    async def test_llamacloud_parse_error(
        self, pdf_parser_service: PDFParserService, parse_pdf_request: ParsePDFToArticleRequest
    ):
        """Test handling of LlamaCloud parsing error"""
        mock_file_obj = MagicMock()
        mock_file_obj.id = "file-123"
        pdf_parser_service.client.files.create = AsyncMock(return_value=mock_file_obj)
        
        pdf_parser_service.client.parsing.parse = AsyncMock(
            side_effect=Exception("LlamaCloud parsing failed")
        )
        
        response = await pdf_parser_service.parse_pdf_to_article(parse_pdf_request)
        
        assert response.success is False
        assert "LlamaCloud parsing failed" in response.message

    @pytest.mark.asyncio
    async def test_article_service_creation_failure(
        self, pdf_parser_service: PDFParserService, parse_pdf_request: ParsePDFToArticleRequest
    ):
        """Test handling when ArticleService fails to create article"""
        mock_file_obj = MagicMock()
        mock_file_obj.id = "file-123"
        pdf_parser_service.client.files.create = AsyncMock(return_value=mock_file_obj)
        
        mock_page = MagicMock()
        mock_page.markdown = "# Title\n\nContent"
        mock_result = MagicMock()
        mock_result.markdown = MagicMock()
        mock_result.markdown.pages = [mock_page]
        pdf_parser_service.client.parsing.parse = AsyncMock(return_value=mock_result)
        
        with patch("app.services.article.pdf_parser_service.ArticleService") as mock_article_service_class:
            mock_article_service = MagicMock()
            mock_article_service_class.return_value = mock_article_service
            mock_article_service.create_or_update_article = AsyncMock(
                return_value=CreateOrUpdateArticleResponse(
                    success=False,
                    id="",
                    message="Database error"
                )
            )
            
            response = await pdf_parser_service.parse_pdf_to_article(parse_pdf_request)
            
            assert response.success is False
            assert "Failed to create article" in response.message
            assert "Database error" in response.message

    @pytest.mark.asyncio
    async def test_page_without_markdown_attribute_skipped(
        self, pdf_parser_service: PDFParserService, parse_pdf_request: ParsePDFToArticleRequest
    ):
        """Test that pages without markdown attribute are skipped"""
        mock_file_obj = MagicMock()
        mock_file_obj.id = "file-123"
        pdf_parser_service.client.files.create = AsyncMock(return_value=mock_file_obj)
        
        # One page with markdown, one without
        mock_page1 = MagicMock()
        mock_page1.markdown = "# Valid Page\n\nContent"
        mock_page2 = MagicMock(spec=[])  # No markdown attribute
        mock_result = MagicMock()
        mock_result.markdown = MagicMock()
        mock_result.markdown.pages = [mock_page1, mock_page2]
        pdf_parser_service.client.parsing.parse = AsyncMock(return_value=mock_result)
        
        with patch("app.services.article.pdf_parser_service.ArticleService") as mock_article_service_class:
            mock_article_service = MagicMock()
            mock_article_service_class.return_value = mock_article_service
            mock_article_service.create_or_update_article = AsyncMock(
                return_value=CreateOrUpdateArticleResponse(
                    success=True,
                    id=TEST_ARTICLE_ID,
                    message="Article created successfully."
                )
            )
            
            response = await pdf_parser_service.parse_pdf_to_article(parse_pdf_request)
            
            assert response.success is True
            # Should still work with the valid page

    @pytest.mark.asyncio
    async def test_temp_file_cleaned_up_on_success(
        self, pdf_parser_service: PDFParserService, parse_pdf_request: ParsePDFToArticleRequest
    ):
        """Test that temporary file is cleaned up after successful parsing"""
        mock_file_obj = MagicMock()
        mock_file_obj.id = "file-123"
        pdf_parser_service.client.files.create = AsyncMock(return_value=mock_file_obj)
        
        mock_page = MagicMock()
        mock_page.markdown = "# Title\n\nContent"
        mock_result = MagicMock()
        mock_result.markdown = MagicMock()
        mock_result.markdown.pages = [mock_page]
        pdf_parser_service.client.parsing.parse = AsyncMock(return_value=mock_result)
        
        with patch("app.services.article.pdf_parser_service.ArticleService") as mock_article_service_class:
            mock_article_service = MagicMock()
            mock_article_service_class.return_value = mock_article_service
            mock_article_service.create_or_update_article = AsyncMock(
                return_value=CreateOrUpdateArticleResponse(
                    success=True,
                    id=TEST_ARTICLE_ID,
                    message="Article created successfully."
                )
            )
            
            with patch("app.services.article.pdf_parser_service.os.path.exists", return_value=True) as mock_exists:
                with patch("app.services.article.pdf_parser_service.os.unlink") as mock_unlink:
                    response = await pdf_parser_service.parse_pdf_to_article(parse_pdf_request)
                    
                    assert response.success is True
                    mock_unlink.assert_called_once()

    @pytest.mark.asyncio
    async def test_temp_file_cleaned_up_on_error(
        self, pdf_parser_service: PDFParserService, parse_pdf_request: ParsePDFToArticleRequest
    ):
        """Test that temporary file is cleaned up even when an error occurs"""
        pdf_parser_service.client.files.create = AsyncMock(
            side_effect=Exception("Upload failed")
        )
        
        with patch("app.services.article.pdf_parser_service.os.path.exists", return_value=True) as mock_exists:
            with patch("app.services.article.pdf_parser_service.os.unlink") as mock_unlink:
                response = await pdf_parser_service.parse_pdf_to_article(parse_pdf_request)
                
                assert response.success is False
                # Cleanup should still be called
                mock_unlink.assert_called_once()

    @pytest.mark.asyncio
    async def test_request_summary_passed_to_article(
        self, pdf_parser_service: PDFParserService
    ):
        """Test that request summary is passed to created article"""
        request = ParsePDFToArticleRequest(
            file_content=TEST_PDF_CONTENT,
            filename=TEST_FILENAME,
            title=None,
            summary="This is the article summary",
            parent="parent-123",
        )
        
        mock_file_obj = MagicMock()
        mock_file_obj.id = "file-123"
        pdf_parser_service.client.files.create = AsyncMock(return_value=mock_file_obj)
        
        mock_page = MagicMock()
        mock_page.markdown = "# Title\n\nContent"
        mock_result = MagicMock()
        mock_result.markdown = MagicMock()
        mock_result.markdown.pages = [mock_page]
        pdf_parser_service.client.parsing.parse = AsyncMock(return_value=mock_result)
        
        with patch("app.services.article.pdf_parser_service.ArticleService") as mock_article_service_class:
            mock_article_service = MagicMock()
            mock_article_service_class.return_value = mock_article_service
            mock_article_service.create_or_update_article = AsyncMock(
                return_value=CreateOrUpdateArticleResponse(
                    success=True,
                    id=TEST_ARTICLE_ID,
                    message="Article created successfully."
                )
            )
            
            response = await pdf_parser_service.parse_pdf_to_article(request)
            
            call_args = mock_article_service.create_or_update_article.call_args
            article_request = call_args[0][0]
            assert article_request.summary == "This is the article summary"
            assert article_request.parent == "parent-123"

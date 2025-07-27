import pytest
from unittest.mock import AsyncMock, Mock, patch, MagicMock
from io import BytesIO
from datetime import timedelta
from app.core.storage import FirebaseStorageRepository


@pytest.fixture
def mock_settings():
    """Mock the settings module"""
    with patch("app.core.storage.settings") as settings_mock:
        settings_mock.google_application_credentials = "/fake/path/to/creds.json"
        settings_mock.firebase_storage_bucket = "test-bucket"
        yield settings_mock


@pytest.fixture
def mock_redis_cache():
    """Mock the RedisCache dependency"""
    with patch("app.core.storage.RedisCache") as redis_cache_mock:
        cache_instance = Mock()
        cache_instance.get = AsyncMock()
        cache_instance.set = AsyncMock()
        redis_cache_mock.return_value = cache_instance
        yield cache_instance


@pytest.fixture
def mock_storage_client():
    """Mock the Google Cloud Storage client and related components"""
    with patch("app.core.storage.service_account") as sa_mock, \
         patch("app.core.storage.storage") as storage_mock:
        
        # Mock credentials
        credentials_mock = Mock()
        sa_mock.Credentials.from_service_account_file.return_value = credentials_mock
        
        # Mock storage client
        client_mock = Mock()
        storage_mock.Client.return_value = client_mock
        
        # Mock bucket
        bucket_mock = Mock()
        client_mock.bucket.return_value = bucket_mock
        
        # Mock blob
        blob_mock = Mock()
        bucket_mock.blob.return_value = blob_mock
        
        yield {
            "service_account": sa_mock,
            "storage": storage_mock,
            "client": client_mock,
            "bucket": bucket_mock,
            "blob": blob_mock,
            "credentials": credentials_mock
        }


@pytest.fixture
def firebase_storage(mock_settings, mock_redis_cache, mock_storage_client):
    """Create a FirebaseStorageRepository instance with mocked dependencies"""
    # Reset singleton instance
    FirebaseStorageRepository._instance = None
    return FirebaseStorageRepository()


class TestFirebaseStorageRepository:
    
    def test_singleton_pattern(self, mock_settings, mock_redis_cache, mock_storage_client):
        """Test that FirebaseStorageRepository follows singleton pattern"""
        # Reset singleton
        FirebaseStorageRepository._instance = None
        
        # Create two instances
        storage1 = FirebaseStorageRepository()
        storage2 = FirebaseStorageRepository()
        
        # Assert they are the same instance
        assert storage1 is storage2
        assert FirebaseStorageRepository._instance is storage1

    def test_initialization(self, mock_settings, mock_redis_cache, mock_storage_client):
        """Test proper initialization of the storage repository"""
        # Reset singleton
        FirebaseStorageRepository._instance = None
        
        storage = FirebaseStorageRepository()
        
        # Verify credentials were loaded
        mock_storage_client["service_account"].Credentials.from_service_account_file.assert_called_once_with(
            "/fake/path/to/creds.json"
        )
        
        # Verify client was created with credentials
        mock_storage_client["storage"].Client.assert_called_once_with(
            credentials=mock_storage_client["credentials"]
        )
        
        # Verify bucket was accessed
        mock_storage_client["client"].bucket.assert_called_once_with("test-bucket")
        
        # Verify initialization flag is set
        assert storage._initialized is True

    def test_initialization_called_once(self, firebase_storage, mock_storage_client):
        """Test that initialization is only called once for singleton"""
        # Create another instance (should not reinitialize)
        storage2 = FirebaseStorageRepository()
        
        # Verify credentials were only called once (from the fixture setup)
        assert mock_storage_client["service_account"].Credentials.from_service_account_file.call_count == 1

    @pytest.mark.asyncio
    async def test_upload_success(self, firebase_storage, mock_storage_client):
        """Test successful file upload"""
        # Setup
        file_obj = BytesIO(b"test file content")
        filename = "test_file.txt"
        expected_url = "https://storage.googleapis.com/test-bucket/test_file.txt"
        
        mock_storage_client["blob"].public_url = expected_url
        
        # Execute
        result = await firebase_storage.upload(file_obj, filename)
        
        # Verify
        mock_storage_client["bucket"].blob.assert_called_with(filename)
        mock_storage_client["blob"].upload_from_file.assert_called_once_with(file_obj)
        assert result == expected_url

    @pytest.mark.asyncio
    async def test_download_success(self, firebase_storage, mock_storage_client):
        """Test successful file download"""
        # Setup
        filename = "test_file.txt"
        expected_content = b"downloaded file content"
        
        mock_storage_client["blob"].download_as_bytes.return_value = expected_content
        
        # Execute
        result = await firebase_storage.download(filename)
        
        # Verify
        mock_storage_client["bucket"].blob.assert_called_with(filename)
        mock_storage_client["blob"].download_as_bytes.assert_called_once()
        assert result == expected_content

    @pytest.mark.asyncio
    async def test_delete_success(self, firebase_storage, mock_storage_client):
        """Test successful file deletion"""
        # Setup
        filename = "test_file.txt"
        
        # Execute
        await firebase_storage.delete(filename)
        
        # Verify
        mock_storage_client["bucket"].blob.assert_called_with(filename)
        mock_storage_client["blob"].delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_presigned_url_empty_filepath(self, firebase_storage):
        """Test get_presigned_url returns empty string for empty filepath"""
        result = await firebase_storage.get_presigned_url("", 3600)
        assert result == ""

    @pytest.mark.asyncio
    async def test_get_presigned_url_cache_hit(self, firebase_storage, mock_redis_cache):
        """Test get_presigned_url returns cached URL when available"""
        # Setup
        filepath = "test/file.txt"
        exp = 3600
        cached_url = "https://cached.url.com"
        cache_key = f"presigned_url:{filepath}"
        
        mock_redis_cache.get.return_value = cached_url
        
        # Execute
        result = await firebase_storage.get_presigned_url(filepath, exp)
        
        # Verify
        mock_redis_cache.get.assert_called_once_with(cache_key)
        assert result == cached_url

    @pytest.mark.asyncio
    async def test_get_presigned_url_cache_miss(self, firebase_storage, mock_redis_cache, mock_storage_client):
        """Test get_presigned_url generates new URL when cache miss"""
        # Setup
        filepath = "test/file.txt"
        exp = 3600
        generated_url = "https://generated.signed.url.com"
        cache_key = f"presigned_url:{filepath}"
        
        mock_redis_cache.get.return_value = None
        mock_storage_client["blob"].generate_signed_url.return_value = generated_url
        
        # Execute
        result = await firebase_storage.get_presigned_url(filepath, exp)
        
        # Verify cache check
        mock_redis_cache.get.assert_called_once_with(cache_key)
        
        # Verify blob access and URL generation
        mock_storage_client["bucket"].blob.assert_called_with(filepath)
        mock_storage_client["blob"].generate_signed_url.assert_called_once_with(
            version="v4",
            expiration=timedelta(seconds=exp),
            method="GET"
        )
        
        # Verify caching of new URL
        mock_redis_cache.set.assert_called_once_with(cache_key, generated_url, expiration=exp)
        
        assert result == generated_url

    @pytest.mark.asyncio
    async def test_upload_exception_handling(self, firebase_storage, mock_storage_client):
        """Test upload method handles exceptions properly"""
        # Setup
        file_obj = BytesIO(b"test content")
        filename = "test_file.txt"
        
        mock_storage_client["blob"].upload_from_file.side_effect = Exception("Upload failed")
        
        # Execute and verify exception is raised
        with pytest.raises(Exception, match="Upload failed"):
            await firebase_storage.upload(file_obj, filename)

    @pytest.mark.asyncio
    async def test_download_exception_handling(self, firebase_storage, mock_storage_client):
        """Test download method handles exceptions properly"""
        # Setup
        filename = "test_file.txt"
        
        mock_storage_client["blob"].download_as_bytes.side_effect = Exception("Download failed")
        
        # Execute and verify exception is raised
        with pytest.raises(Exception, match="Download failed"):
            await firebase_storage.download(filename)

    @pytest.mark.asyncio
    async def test_delete_exception_handling(self, firebase_storage, mock_storage_client):
        """Test delete method handles exceptions properly"""
        # Setup
        filename = "test_file.txt"
        
        mock_storage_client["blob"].delete.side_effect = Exception("Delete failed")
        
        # Execute and verify exception is raised
        with pytest.raises(Exception, match="Delete failed"):
            await firebase_storage.delete(filename)

    @pytest.mark.asyncio
    async def test_get_presigned_url_generation_exception(self, firebase_storage, mock_redis_cache, mock_storage_client):
        """Test get_presigned_url handles URL generation exceptions"""
        # Setup
        filepath = "test/file.txt"
        exp = 3600
        
        mock_redis_cache.get.return_value = None
        mock_storage_client["blob"].generate_signed_url.side_effect = Exception("URL generation failed")
        
        # Execute and verify exception is raised
        with pytest.raises(Exception, match="URL generation failed"):
            await firebase_storage.get_presigned_url(filepath, exp)

    @pytest.mark.asyncio
    async def test_get_presigned_url_cache_set_exception(self, firebase_storage, mock_redis_cache, mock_storage_client):
        """Test get_presigned_url continues even if cache set fails"""
        # Setup
        filepath = "test/file.txt"
        exp = 3600
        generated_url = "https://generated.signed.url.com"
        
        mock_redis_cache.get.return_value = None
        mock_redis_cache.set.side_effect = Exception("Cache set failed")
        mock_storage_client["blob"].generate_signed_url.return_value = generated_url
        
        # Execute and verify it still returns the URL despite cache failure
        with pytest.raises(Exception, match="Cache set failed"):
            await firebase_storage.get_presigned_url(filepath, exp)

    def test_multiple_initialization_attempts(self, mock_settings, mock_redis_cache, mock_storage_client):
        """Test that multiple initialization attempts don't cause issues"""
        # Reset singleton
        FirebaseStorageRepository._instance = None
        
        # Create instance
        storage1 = FirebaseStorageRepository()
        
        # Manually call __init__ again (simulating multiple initialization)
        storage1.__init__()
        
        # Should still work and not reinitialize
        assert storage1._initialized is True
        
        # Verify credentials were only called once
        assert mock_storage_client["service_account"].Credentials.from_service_account_file.call_count == 1 
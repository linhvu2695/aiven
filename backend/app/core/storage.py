from google.cloud import storage
from google.oauth2 import service_account
from typing import BinaryIO
from app.core.config import settings
from datetime import timedelta
from app.core.cache import RedisCache
from app.utils.string.string_utils import is_empty_string

class FirebaseStorageRepository:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(FirebaseStorageRepository, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, '_initialized') and self._initialized:
            return
        credentials = service_account.Credentials.from_service_account_file(
            settings.google_application_credentials
        )
        self.client = storage.Client(credentials=credentials)
        self.bucket = self.client.bucket(settings.firebase_storage_bucket)
        self._initialized = True

    async def upload(self, file_obj: BinaryIO, filename: str) -> str:
        blob = self.bucket.blob(filename)
        blob.upload_from_file(file_obj)
        return blob.public_url

    async def download(self, filename: str) -> bytes:
        blob = self.bucket.blob(filename)
        return blob.download_as_bytes()
    
    async def get_presigned_url(self, filepath: str, exp: int) -> str:
        """
        Generate a presigned (signed) URL for accessing a file in Firebase Storage.

        Args:
            filepath (str): The path to the file in the storage bucket.
            exp (int): The expiration time in seconds for the presigned URL.

        Returns:
            str: The presigned URL as a string, or an empty string if filepath is not provided.
        """  
        if is_empty_string(filepath):
            return ""
        cache_key = f"presigned_url:{filepath}"
        cached_url = await RedisCache().get(cache_key)
        if cached_url:
            return cached_url
        
        blob = self.bucket.blob(filepath)
        url = blob.generate_signed_url(
            version="v4",
            expiration=timedelta(seconds=exp),
            method="GET"
        )
        await RedisCache().set(cache_key, url, expiration=exp)
        return url

    async def delete(self, filename: str) -> None:
        blob = self.bucket.blob(filename)
        blob.delete()
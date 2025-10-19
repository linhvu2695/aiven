import pytest
from httpx import AsyncClient, ASGITransport
from fastapi import FastAPI
from unittest.mock import patch, AsyncMock
from datetime import datetime, timezone
from bson import ObjectId

from app.api.user_api import router
from app.classes.user import GetUserByIdResponse, UserInfo, DeleteUserResponse


app = FastAPI()
app.include_router(router, prefix="/users")


class TestGetUserApi:
    @pytest.mark.asyncio
    async def test_get_user_success(self):
        """Test successful user retrieval"""
        user_id = str(ObjectId())
        
        mock_user = UserInfo(
            id=user_id,
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password_value",
            password_salt="salt_value",
            hash_algorithm="pbkdf2_sha256",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            disabled=False
        )
        
        mock_response = GetUserByIdResponse(
            success=True,
            user=mock_user,
            status_code=200,
            message=""
        )
        
        with patch("app.services.user.user_repository.UserRepository.get_user_by_id", new=AsyncMock(return_value=mock_response)):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                response = await ac.get(f"/users/{user_id}")
                
                assert response.status_code == 200
                data = response.json()
                
                # Verify response structure
                assert data["success"] is True
                assert data["status_code"] == 200
                assert data["message"] == ""
                assert data["user"] is not None
                
                # Verify user data
                assert data["user"]["id"] == user_id
                assert data["user"]["username"] == "testuser"
                assert data["user"]["email"] == "test@example.com"
                assert data["user"]["disabled"] is False
                
                # Verify sensitive fields are removed
                assert "password_hash" not in data["user"]
                assert "password_salt" not in data["user"]
                assert "hash_algorithm" not in data["user"]
                
                # Verify timestamps are present
                assert "created_at" in data["user"]
                assert "updated_at" in data["user"]


    @pytest.mark.asyncio
    async def test_get_user_not_found(self):
        """Test user retrieval when user does not exist"""
        user_id = str(ObjectId())
        
        mock_response = GetUserByIdResponse(
            success=True,
            user=None,
            status_code=404,
            message="User not found"
        )
        
        with patch("app.services.user.user_repository.UserRepository.get_user_by_id", new=AsyncMock(return_value=mock_response)):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                response = await ac.get(f"/users/{user_id}")
                
                assert response.status_code == 404
                data = response.json()
                assert data["detail"] == "User not found"


    @pytest.mark.asyncio
    async def test_get_user_invalid_id_format(self):
        """Test user retrieval with invalid ID format"""
        invalid_id = "invalid_id_format"
        
        mock_response = GetUserByIdResponse(
            success=False,
            user=None,
            status_code=400,
            message="Invalid user ID format"
        )
        
        with patch("app.services.user.user_repository.UserRepository.get_user_by_id", new=AsyncMock(return_value=mock_response)):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                response = await ac.get(f"/users/{invalid_id}")
                
                assert response.status_code == 400
                data = response.json()
                assert data["detail"] == "Invalid user ID format"


    @pytest.mark.asyncio
    async def test_get_user_database_error(self):
        """Test user retrieval when database error occurs"""
        user_id = str(ObjectId())
        
        mock_response = GetUserByIdResponse(
            success=False,
            user=None,
            status_code=500,
            message="Failed to get user by id: Database connection error"
        )
        
        with patch("app.services.user.user_repository.UserRepository.get_user_by_id", new=AsyncMock(return_value=mock_response)):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                response = await ac.get(f"/users/{user_id}")
                
                assert response.status_code == 500
                data = response.json()
                assert "Failed to get user by id" in data["detail"]


    @pytest.mark.asyncio
    async def test_get_user_disabled_user(self):
        """Test that disabled users can still be retrieved (no filtering at repository level)"""
        user_id = str(ObjectId())
        
        mock_user = UserInfo(
            id=user_id,
            username="disableduser",
            email="disabled@example.com",
            password_hash="hashed_password_value",
            password_salt="salt_value",
            hash_algorithm="pbkdf2_sha256",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            disabled=True
        )
        
        mock_response = GetUserByIdResponse(
            success=True,
            user=mock_user,
            status_code=200,
            message=""
        )
        
        with patch("app.services.user.user_repository.UserRepository.get_user_by_id", new=AsyncMock(return_value=mock_response)):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                response = await ac.get(f"/users/{user_id}")
                
                assert response.status_code == 200
                data = response.json()
                
                assert data["success"] is True
                assert data["user"]["disabled"] is True
                assert data["user"]["username"] == "disableduser"
                
                # Verify sensitive fields are still removed even for disabled users
                assert "password_hash" not in data["user"]
                assert "password_salt" not in data["user"]
                assert "hash_algorithm" not in data["user"]


    @pytest.mark.asyncio
    async def test_get_user_response_excludes_only_sensitive_fields(self):
        """Test that only password-related fields are excluded from response"""
        user_id = str(ObjectId())
        created_at = datetime.now(timezone.utc)
        updated_at = datetime.now(timezone.utc)
        
        mock_user = UserInfo(
            id=user_id,
            username="testuser",
            email="test@example.com",
            password_hash="should_be_removed",
            password_salt="should_be_removed",
            hash_algorithm="should_be_removed",
            created_at=created_at,
            updated_at=updated_at,
            disabled=False
        )
        
        mock_response = GetUserByIdResponse(
            success=True,
            user=mock_user,
            status_code=200,
            message=""
        )
        
        with patch("app.services.user.user_repository.UserRepository.get_user_by_id", new=AsyncMock(return_value=mock_response)):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                response = await ac.get(f"/users/{user_id}")
                
                assert response.status_code == 200
                data = response.json()
                
                user_data = data["user"]
                
                # Fields that SHOULD be present
                assert "id" in user_data
                assert "username" in user_data
                assert "email" in user_data
                assert "created_at" in user_data
                assert "updated_at" in user_data
                assert "disabled" in user_data
                
                # Fields that SHOULD NOT be present
                assert "password_hash" not in user_data
                assert "password_salt" not in user_data
                assert "hash_algorithm" not in user_data


class TestDeleteUserApi:
    
    @pytest.mark.asyncio
    async def test_delete_user_success(self):
        """Test successful user deletion"""
        user_id = str(ObjectId())
        
        mock_response = DeleteUserResponse(
            success=True,
            message="User deleted successfully",
            status_code=200
        )

        mock_delete = AsyncMock(return_value=mock_response)
        with patch("app.services.user.user_repository.UserRepository.delete_user", new=mock_delete):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                response = await ac.delete(f"/users/{user_id}")
                
                assert response.status_code == 200
                data = response.json()
                
                assert data["success"] is True
                assert data["message"] == "User deleted successfully"
                assert data["status_code"] == 200
                mock_delete.assert_called_once_with(user_id)


    @pytest.mark.asyncio
    async def test_delete_user_not_found(self):
        """Test deleting a user that does not exist"""
        user_id = str(ObjectId())
        
        mock_response = DeleteUserResponse(
            success=False,
            message="User not found",
            status_code=404
        )
        
        with patch("app.services.user.user_repository.UserRepository.delete_user", new=AsyncMock(return_value=mock_response)):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                response = await ac.delete(f"/users/{user_id}")
                
                assert response.status_code == 404
                data = response.json()
                assert data["detail"] == "User not found"


    @pytest.mark.asyncio
    async def test_delete_user_invalid_id_format(self):
        """Test deleting a user with invalid ID format"""
        invalid_id = "invalid_id_format"
        
        mock_response = DeleteUserResponse(
            success=False,
            message="Invalid user ID format",
            status_code=400
        )
        
        with patch("app.services.user.user_repository.UserRepository.delete_user", new=AsyncMock(return_value=mock_response)):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                response = await ac.delete(f"/users/{invalid_id}")
                
                assert response.status_code == 400
                data = response.json()
                assert data["detail"] == "Invalid user ID format"


    @pytest.mark.asyncio
    async def test_delete_user_database_error(self):
        """Test user deletion when database error occurs"""
        user_id = str(ObjectId())
        
        mock_response = DeleteUserResponse(
            success=False,
            message="Failed to delete user: Database connection error",
            status_code=500
        )
        
        with patch("app.services.user.user_repository.UserRepository.delete_user", new=AsyncMock(return_value=mock_response)):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                response = await ac.delete(f"/users/{user_id}")
                
                assert response.status_code == 500
                data = response.json()
                assert "Failed to delete user" in data["detail"]


    @pytest.mark.asyncio
    async def test_delete_user_deletion_failure(self):
        """Test user deletion when delete operation fails"""
        user_id = str(ObjectId())
        
        mock_response = DeleteUserResponse(
            success=False,
            message="Failed to delete user",
            status_code=500
        )
        
        with patch("app.services.user.user_repository.UserRepository.delete_user", new=AsyncMock(return_value=mock_response)):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                response = await ac.delete(f"/users/{user_id}")
                
                assert response.status_code == 500
                data = response.json()
                assert data["detail"] == "Failed to delete user"


    @pytest.mark.asyncio
    async def test_delete_user_disabled_user(self):
        """Test that disabled users can be deleted"""
        user_id = str(ObjectId())
        
        mock_response = DeleteUserResponse(
            success=True,
            message="User deleted successfully",
            status_code=200
        )
        
        with patch("app.services.user.user_repository.UserRepository.delete_user", new=AsyncMock(return_value=mock_response)):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                response = await ac.delete(f"/users/{user_id}")
                
                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True
                assert data["message"] == "User deleted successfully"
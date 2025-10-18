import pytest
from datetime import datetime, timezone
from unittest.mock import patch, AsyncMock
from app.services.user.user_repository import UserRepository, HASH_ALGORITHM, HASH_ITERATIONS
from app.classes.user import CreateUserRequest, CreateUserResponse


@pytest.fixture
def user_repository():
    """Create a fresh instance for each test"""
    # Reset the singleton instance
    UserRepository._instance = None
    return UserRepository()


@pytest.fixture
def create_user_request():
    """Valid create user request"""
    return CreateUserRequest(
        username="testuser",
        email="test@example.com",
        password="SecurePassword123!"
    )


class TestUserRepositorySingleton:

    def test_singleton_instance(self):
        """Test that UserRepository is a singleton"""
        repo1 = UserRepository()
        repo2 = UserRepository()
        assert repo1 is repo2


class TestUserRepositoryCreateUser:

    @pytest.mark.asyncio
    async def test_create_user_success(self, user_repository, create_user_request):
        """Test successful user creation"""
        mock_user_id = "user_12345"
        
        with patch("app.services.user.user_repository.insert_document", new_callable=AsyncMock, return_value=mock_user_id) as mock_insert:
            response = await user_repository.create_user(create_user_request)
            
            # Verify response
            assert isinstance(response, CreateUserResponse)
            assert response.success is True
            assert response.user_id == mock_user_id
            assert response.message == "User created successfully"
            
            # Verify insert_document was called once
            mock_insert.assert_called_once()
            
            # Verify the data passed to insert_document
            call_args = mock_insert.call_args
            collection_name = call_args[0][0]
            user_data = call_args[0][1]
            
            assert collection_name == "users"
            assert user_data["username"] == "testuser"
            assert user_data["email"] == "test@example.com"
            assert user_data["hash_algorithm"] == HASH_ALGORITHM
            assert "password_hash" in user_data
            assert "password_salt" in user_data
            assert len(user_data["password_salt"]) == 64  # 32 bytes = 64 hex chars
            assert "created_at" in user_data
            assert "updated_at" in user_data
            assert isinstance(user_data["created_at"], datetime)
            assert isinstance(user_data["updated_at"], datetime)

    @pytest.mark.asyncio
    async def test_create_user_password_hashing(self, user_repository):
        """Test that password is properly hashed with salt"""
        request1 = CreateUserRequest(
            username="user1",
            email="user1@example.com",
            password="SamePassword123!"
        )
        request2 = CreateUserRequest(
            username="user2",
            email="user2@example.com",
            password="SamePassword123!"
        )
        
        with patch("app.services.user.user_repository.insert_document", new_callable=AsyncMock, return_value="user_id") as mock_insert:
            await user_repository.create_user(request1)
            await user_repository.create_user(request2)
            
            # Get the user data from both calls
            call1_data = mock_insert.call_args_list[0][0][1]
            call2_data = mock_insert.call_args_list[1][0][1]
            
            # Same password should result in different hashes due to different salts
            assert call1_data["password_salt"] != call2_data["password_salt"]
            assert call1_data["password_hash"] != call2_data["password_hash"]
            
            # Both should have proper length
            assert len(call1_data["password_hash"]) > 0
            assert len(call2_data["password_hash"]) > 0

    @pytest.mark.asyncio
    async def test_create_user_insert_failure(self, user_repository, create_user_request):
        """Test user creation when insert_document returns None"""
        with patch("app.services.user.user_repository.insert_document", new_callable=AsyncMock, return_value=None):
            response = await user_repository.create_user(create_user_request)
            
            assert isinstance(response, CreateUserResponse)
            assert response.success is False
            assert response.user_id == ""
            assert response.message == "Failed to insert user"

    @pytest.mark.asyncio
    async def test_create_user_insert_empty_output_id(self, user_repository, create_user_request):
        """Test user creation when insert_document returns empty string"""
        with patch("app.services.user.user_repository.insert_document", new_callable=AsyncMock, return_value=""):
            response = await user_repository.create_user(create_user_request)
            
            assert isinstance(response, CreateUserResponse)
            assert response.success is False
            assert response.user_id == ""
            assert response.message == "Failed to insert user"

    @pytest.mark.asyncio
    async def test_create_user_database_exception(self, user_repository, create_user_request):
        """Test user creation when database throws an exception"""
        with patch("app.services.user.user_repository.insert_document", new_callable=AsyncMock, side_effect=Exception("Database connection error")):
            response = await user_repository.create_user(create_user_request)
            
            assert isinstance(response, CreateUserResponse)
            assert response.success is False
            assert response.user_id == ""
            assert response.message == "Failed to insert user into DB"

    @pytest.mark.asyncio
    async def test_create_user_with_special_characters(self, user_repository):
        """Test user creation with special characters in password"""
        request = CreateUserRequest(
            username="specialuser",
            email="special@example.com",
            password="P@ssw0rd!#$%^&*()"
        )
        
        with patch("app.services.user.user_repository.insert_document", new_callable=AsyncMock, return_value="user_id") as mock_insert:
            response = await user_repository.create_user(request)
            
            assert response.success is True
            
            # Verify that password was hashed properly
            user_data = mock_insert.call_args[0][1]
            assert "password_hash" in user_data
            assert len(user_data["password_hash"]) > 0
            # Password should not be stored in plain text
            assert "P@ssw0rd!#$%^&*()" not in str(user_data)

    @pytest.mark.asyncio
    async def test_create_user_password_hash_algorithm_stored(self, user_repository, create_user_request):
        """Test that the hash algorithm is properly stored"""
        with patch("app.services.user.user_repository.insert_document", new_callable=AsyncMock, return_value="user_id") as mock_insert:
            response = await user_repository.create_user(create_user_request)
            
            assert response.success is True
            
            user_data = mock_insert.call_args[0][1]
            assert user_data["hash_algorithm"] == HASH_ALGORITHM

    @pytest.mark.asyncio
    async def test_create_user_timestamps_are_utc(self, user_repository, create_user_request):
        """Test that timestamps are in UTC timezone"""
        with patch("app.services.user.user_repository.insert_document", new_callable=AsyncMock, return_value="user_id") as mock_insert:
            response = await user_repository.create_user(create_user_request)
            
            assert response.success is True
            
            user_data = mock_insert.call_args[0][1]
            assert user_data["created_at"].tzinfo == timezone.utc
            assert user_data["updated_at"].tzinfo == timezone.utc

    @pytest.mark.asyncio
    async def test_create_user_different_users_same_time(self, user_repository):
        """Test creating multiple users handles each independently"""
        request1 = CreateUserRequest(
            username="user1",
            email="user1@example.com",
            password="Password1!"
        )
        request2 = CreateUserRequest(
            username="user2",
            email="user2@example.com",
            password="Password2!"
        )
        
        with patch("app.services.user.user_repository.insert_document", new_callable=AsyncMock) as mock_insert:
            mock_insert.side_effect = ["user_id_1", "user_id_2"]
            
            response1 = await user_repository.create_user(request1)
            response2 = await user_repository.create_user(request2)
            
            assert response1.success is True
            assert response1.user_id == "user_id_1"
            assert response2.success is True
            assert response2.user_id == "user_id_2"
            
            # Verify both calls had different data
            call1_data = mock_insert.call_args_list[0][0][1]
            call2_data = mock_insert.call_args_list[1][0][1]
            
            assert call1_data["username"] == "user1"
            assert call2_data["username"] == "user2"
            assert call1_data["email"] == "user1@example.com"
            assert call2_data["email"] == "user2@example.com"


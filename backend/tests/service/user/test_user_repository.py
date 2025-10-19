import pytest
from datetime import datetime, timezone
from unittest.mock import patch, AsyncMock
from app.services.user.user_repository import UserRepository, HASH_ALGORITHM, HASH_ITERATIONS
from app.classes.user import CreateUserRequest, CreateUserResponse, GetUserByEmailRequest, GetUserByUsernameRequest, GetUserByIdResponse


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
    async def test_create_user_success(self, user_repository: UserRepository, create_user_request: CreateUserRequest):
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
    async def test_create_user_password_hashing(self, user_repository: UserRepository):
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
    async def test_create_user_insert_failure(self, user_repository: UserRepository, create_user_request: CreateUserRequest):
        """Test user creation when insert_document returns None"""
        with patch("app.services.user.user_repository.insert_document", new_callable=AsyncMock, return_value=None):
            response = await user_repository.create_user(create_user_request)
            
            assert isinstance(response, CreateUserResponse)
            assert response.success is False
            assert response.user_id == ""
            assert response.message == "Failed to insert user"

    @pytest.mark.asyncio
    async def test_create_user_insert_empty_output_id(self, user_repository: UserRepository, create_user_request: CreateUserRequest):
        """Test user creation when insert_document returns empty string"""
        with patch("app.services.user.user_repository.insert_document", new_callable=AsyncMock, return_value=""):
            response = await user_repository.create_user(create_user_request)
            
            assert isinstance(response, CreateUserResponse)
            assert response.success is False
            assert response.user_id == ""
            assert response.message == "Failed to insert user"

    @pytest.mark.asyncio
    async def test_create_user_database_exception(self, user_repository: UserRepository, create_user_request: CreateUserRequest):
        """Test user creation when database throws an exception"""
        with patch("app.services.user.user_repository.insert_document", new_callable=AsyncMock, side_effect=Exception("Database connection error")):
            response = await user_repository.create_user(create_user_request)
            
            assert isinstance(response, CreateUserResponse)
            assert response.success is False
            assert response.user_id == ""
            assert response.message == "Failed to insert user into DB"

    @pytest.mark.asyncio
    async def test_create_user_with_special_characters(self, user_repository: UserRepository):
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
    async def test_create_user_password_hash_algorithm_stored(self, user_repository: UserRepository, create_user_request: CreateUserRequest):
        """Test that the hash algorithm is properly stored"""
        with patch("app.services.user.user_repository.insert_document", new_callable=AsyncMock, return_value="user_id") as mock_insert:
            response = await user_repository.create_user(create_user_request)
            
            assert response.success is True
            
            user_data = mock_insert.call_args[0][1]
            assert user_data["hash_algorithm"] == HASH_ALGORITHM

    @pytest.mark.asyncio
    async def test_create_user_timestamps_are_utc(self, user_repository: UserRepository, create_user_request: CreateUserRequest):
        """Test that timestamps are in UTC timezone"""
        with patch("app.services.user.user_repository.insert_document", new_callable=AsyncMock, return_value="user_id") as mock_insert:
            response = await user_repository.create_user(create_user_request)
            
            assert response.success is True
            
            user_data = mock_insert.call_args[0][1]
            assert user_data["created_at"].tzinfo == timezone.utc
            assert user_data["updated_at"].tzinfo == timezone.utc

    @pytest.mark.asyncio
    async def test_create_user_different_users_same_time(self, user_repository: UserRepository):
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


class TestUserRepositoryGetUserByEmail:

    @pytest.mark.asyncio
    async def test_get_user_by_email_success(self, user_repository: UserRepository):
        """Test successful user retrieval by email"""
        mock_user_data = {
            "_id": "user_123",
            "username": "testuser",
            "email": "test@example.com",
            "password_hash": "hashed_password",
            "password_salt": "salt_value",
            "hash_algorithm": HASH_ALGORITHM,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "disabled": False
        }
        
        with patch("app.services.user.user_repository.find_documents_with_filters", new_callable=AsyncMock, return_value=[mock_user_data]) as mock_find:
            request = GetUserByEmailRequest(email="test@example.com", include_disabled=False)
            response = await user_repository.get_user_by_email(request)
            
            # Verify response
            assert response.success is True
            assert response.user is not None
            assert response.user.email == "test@example.com"
            assert response.user.username == "testuser"
            assert response.user.id == "user_123"
            assert response.user.disabled is False
            assert response.message == ""
            
            # Verify the correct filters were used
            mock_find.assert_called_once()
            call_args = mock_find.call_args
            collection_name = call_args[0][0]
            filters = call_args[0][1]
            
            assert collection_name == "users"
            assert filters["email"] == "test@example.com"
            assert filters["disabled"] is False
            assert call_args[1]["limit"] == 1

    @pytest.mark.asyncio
    async def test_get_user_by_email_not_found(self, user_repository: UserRepository):
        """Test user retrieval when user does not exist (successful query, no results)"""
        with patch("app.services.user.user_repository.find_documents_with_filters", new_callable=AsyncMock, return_value=[]) as mock_find:
            request = GetUserByEmailRequest(email="nonexistent@example.com", include_disabled=False)
            response = await user_repository.get_user_by_email(request)
            
            assert response.success is True
            assert response.user is None
            assert response.message == "User not found"
            
            # Verify find was called with correct parameters
            mock_find.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_user_by_email_include_disabled_false(self, user_repository: UserRepository):
        """Test that include_disabled=False filters for non-disabled users"""
        mock_user_data = {
            "_id": "user_123",
            "username": "activeuser",
            "email": "active@example.com",
            "password_hash": "hashed_password",
            "password_salt": "salt_value",
            "hash_algorithm": HASH_ALGORITHM,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "disabled": False
        }
        
        with patch("app.services.user.user_repository.find_documents_with_filters", new_callable=AsyncMock, return_value=[mock_user_data]) as mock_find:
            request = GetUserByEmailRequest(email="active@example.com", include_disabled=False)
            response = await user_repository.get_user_by_email(request)
            
            assert response.success is True
            
            # Verify the filter includes disabled=False
            call_args = mock_find.call_args
            filters = call_args[0][1]
            assert "disabled" in filters
            assert filters["disabled"] is False

    @pytest.mark.asyncio
    async def test_get_user_by_email_include_disabled_true(self, user_repository: UserRepository):
        """Test that include_disabled=True does not filter by disabled status"""
        mock_user_data = {
            "_id": "user_123",
            "username": "disableduser",
            "email": "disabled@example.com",
            "password_hash": "hashed_password",
            "password_salt": "salt_value",
            "hash_algorithm": HASH_ALGORITHM,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "disabled": True
        }
        
        with patch("app.services.user.user_repository.find_documents_with_filters", new_callable=AsyncMock, return_value=[mock_user_data]) as mock_find:
            request = GetUserByEmailRequest(email="disabled@example.com", include_disabled=True)
            response = await user_repository.get_user_by_email(request)
            
            assert response.success is True
            assert response.user is not None
            assert response.user.disabled is True
            
            # Verify the filter does NOT include disabled field
            call_args = mock_find.call_args
            filters = call_args[0][1]
            assert "disabled" not in filters
            assert "email" in filters

    @pytest.mark.asyncio
    async def test_get_user_by_email_database_exception(self, user_repository: UserRepository):
        """Test user retrieval when database throws an exception"""
        with patch("app.services.user.user_repository.find_documents_with_filters", new_callable=AsyncMock, side_effect=Exception("Database connection error")) as mock_find:
            request = GetUserByEmailRequest(email="test@example.com", include_disabled=False)
            response = await user_repository.get_user_by_email(request)
            
            assert response.success is False
            assert response.user is None
            assert "Failed to get user by email" in response.message
            assert "Database connection error" in response.message

    @pytest.mark.asyncio
    async def test_get_user_by_email_returns_none(self, user_repository: UserRepository):
        """Test user retrieval when find_documents_with_filters returns None (successful query, no results)"""
        with patch("app.services.user.user_repository.find_documents_with_filters", new_callable=AsyncMock, return_value=None) as mock_find:
            request = GetUserByEmailRequest(email="test@example.com", include_disabled=False)
            response = await user_repository.get_user_by_email(request)
            
            assert response.success is True
            assert response.user is None
            assert response.message == "User not found"


class TestUserRepositoryGetUserByUsername:

    @pytest.mark.asyncio
    async def test_get_user_by_username_success(self, user_repository: UserRepository):
        """Test successful user retrieval by username"""
        mock_user_data = {
            "_id": "user_123",
            "username": "testuser",
            "email": "test@example.com",
            "password_hash": "hashed_password",
            "password_salt": "salt_value",
            "hash_algorithm": HASH_ALGORITHM,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "disabled": False
        }
        
        with patch("app.services.user.user_repository.find_documents_with_filters", new_callable=AsyncMock, return_value=[mock_user_data]) as mock_find:
            request = GetUserByUsernameRequest(username="testuser", include_disabled=False)
            response = await user_repository.get_user_by_username(request)
            
            # Verify response
            assert response.success is True
            assert response.user is not None
            assert response.user.username == "testuser"
            assert response.user.email == "test@example.com"
            assert response.user.id == "user_123"
            assert response.user.disabled is False
            assert response.message == ""
            
            # Verify the correct filters were used
            mock_find.assert_called_once()
            call_args = mock_find.call_args
            collection_name = call_args[0][0]
            filters = call_args[0][1]
            
            assert collection_name == "users"
            assert filters["username"] == "testuser"
            assert filters["disabled"] is False
            assert call_args[1]["limit"] == 1

    @pytest.mark.asyncio
    async def test_get_user_by_username_not_found(self, user_repository: UserRepository):
        """Test user retrieval when user does not exist (successful query, no results)"""
        with patch("app.services.user.user_repository.find_documents_with_filters", new_callable=AsyncMock, return_value=[]) as mock_find:
            request = GetUserByUsernameRequest(username="nonexistent", include_disabled=False)
            response = await user_repository.get_user_by_username(request)
            
            assert response.success is True
            assert response.user is None
            assert response.message == "User not found"
            
            # Verify find was called with correct parameters
            mock_find.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_user_by_username_include_disabled_false(self, user_repository: UserRepository):
        """Test that include_disabled=False filters for non-disabled users"""
        mock_user_data = {
            "_id": "user_123",
            "username": "activeuser",
            "email": "active@example.com",
            "password_hash": "hashed_password",
            "password_salt": "salt_value",
            "hash_algorithm": HASH_ALGORITHM,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "disabled": False
        }
        
        with patch("app.services.user.user_repository.find_documents_with_filters", new_callable=AsyncMock, return_value=[mock_user_data]) as mock_find:
            request = GetUserByUsernameRequest(username="activeuser", include_disabled=False)
            response = await user_repository.get_user_by_username(request)
            
            assert response.success is True
            
            # Verify the filter includes disabled=False
            call_args = mock_find.call_args
            filters = call_args[0][1]
            assert "disabled" in filters
            assert filters["disabled"] is False

    @pytest.mark.asyncio
    async def test_get_user_by_username_include_disabled_true(self, user_repository: UserRepository):
        """Test that include_disabled=True does not filter by disabled status"""
        mock_user_data = {
            "_id": "user_123",
            "username": "disableduser",
            "email": "disabled@example.com",
            "password_hash": "hashed_password",
            "password_salt": "salt_value",
            "hash_algorithm": HASH_ALGORITHM,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "disabled": True
        }
        
        with patch("app.services.user.user_repository.find_documents_with_filters", new_callable=AsyncMock, return_value=[mock_user_data]) as mock_find:
            request = GetUserByUsernameRequest(username="disableduser", include_disabled=True)
            response = await user_repository.get_user_by_username(request)
            
            assert response.success is True
            assert response.user is not None
            assert response.user.disabled is True
            
            # Verify the filter does NOT include disabled field
            call_args = mock_find.call_args
            filters = call_args[0][1]
            assert "disabled" not in filters
            assert "username" in filters

    @pytest.mark.asyncio
    async def test_get_user_by_username_database_exception(self, user_repository: UserRepository):
        """Test user retrieval when database throws an exception"""
        with patch("app.services.user.user_repository.find_documents_with_filters", new_callable=AsyncMock, side_effect=Exception("Database connection error")) as mock_find:
            request = GetUserByUsernameRequest(username="testuser", include_disabled=False)
            response = await user_repository.get_user_by_username(request)
            
            assert response.success is False
            assert response.user is None
            assert "Failed to get user by username" in response.message
            assert "Database connection error" in response.message

    @pytest.mark.asyncio
    async def test_get_user_by_username_returns_none(self, user_repository: UserRepository):
        """Test user retrieval when find_documents_with_filters returns None (successful query, no results)"""
        with patch("app.services.user.user_repository.find_documents_with_filters", new_callable=AsyncMock, return_value=None) as mock_find:
            request = GetUserByUsernameRequest(username="testuser", include_disabled=False)
            response = await user_repository.get_user_by_username(request)
            
            assert response.success is True
            assert response.user is None
            assert response.message == "User not found"


class TestUserRepositoryGetUserById:

    @pytest.mark.asyncio
    async def test_get_user_by_id_success(self, user_repository: UserRepository):
        """Test successful user retrieval by ID"""
        from bson import ObjectId
        
        # Use a valid ObjectId format
        valid_id = str(ObjectId())
        
        mock_user_data = {
            "_id": valid_id,
            "username": "testuser",
            "email": "test@example.com",
            "password_hash": "hashed_password",
            "password_salt": "salt_value",
            "hash_algorithm": HASH_ALGORITHM,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "disabled": False
        }
        
        with patch("app.services.user.user_repository.get_document", new_callable=AsyncMock, return_value=mock_user_data) as mock_get:
            response = await user_repository.get_user_by_id(valid_id)
            
            # Verify response
            assert response.success is True
            assert response.status_code == 200
            assert response.user is not None
            assert response.user.id == valid_id
            assert response.user.username == "testuser"
            assert response.user.email == "test@example.com"
            assert response.user.disabled is False
            assert response.message == ""
            
            # Verify get_document was called with correct parameters
            mock_get.assert_called_once_with("users", valid_id)

    @pytest.mark.asyncio
    async def test_get_user_by_id_not_found(self, user_repository: UserRepository):
        """Test user retrieval when user does not exist"""
        from bson import ObjectId
        
        # Use a valid ObjectId format
        valid_id = str(ObjectId())
        
        with patch("app.services.user.user_repository.get_document", new_callable=AsyncMock, return_value=None) as mock_get:
            response = await user_repository.get_user_by_id(valid_id)
            
            assert response.success is True
            assert response.status_code == 404
            assert response.user is None
            assert response.message == "User not found"

    @pytest.mark.asyncio
    async def test_get_user_by_id_invalid_id_format(self, user_repository: UserRepository):
        """Test user retrieval with invalid ID format"""
        response = await user_repository.get_user_by_id("invalid_id_format")
        
        assert response.success is False
        assert response.status_code == 400
        assert response.user is None
        assert "Invalid user ID format" in response.message

    @pytest.mark.asyncio
    async def test_get_user_by_id_database_exception(self, user_repository: UserRepository):
        """Test user retrieval when database throws an exception"""
        from bson import ObjectId
        
        # Use a valid ObjectId format
        valid_id = str(ObjectId())
        
        with patch("app.services.user.user_repository.get_document", new_callable=AsyncMock, side_effect=Exception("Database connection error")) as mock_get:
            response = await user_repository.get_user_by_id(valid_id)
            
            assert response.success is False
            assert response.status_code == 500
            assert response.user is None
            assert "Failed to get user by id" in response.message
            assert "Database connection error" in response.message

    @pytest.mark.asyncio
    async def test_get_user_by_id_returns_disabled_user(self, user_repository: UserRepository):
        """Test that get_user_by_id returns disabled users (no filtering)"""
        from bson import ObjectId
        
        # Use a valid ObjectId format
        valid_id = str(ObjectId())
        
        mock_user_data = {
            "_id": valid_id,
            "username": "disableduser",
            "email": "disabled@example.com",
            "password_hash": "hashed_password",
            "password_salt": "salt_value",
            "hash_algorithm": HASH_ALGORITHM,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "disabled": True
        }
        
        with patch("app.services.user.user_repository.get_document", new_callable=AsyncMock, return_value=mock_user_data) as mock_get:
            response = await user_repository.get_user_by_id(valid_id)
            
            assert response.success is True
            assert response.status_code == 200
            assert response.user is not None
            assert response.user.disabled is True
            assert response.user.username == "disableduser"

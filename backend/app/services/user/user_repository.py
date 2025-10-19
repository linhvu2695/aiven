from datetime import datetime, timezone
import secrets
import hashlib
from typing import Dict, Any

from bson import ObjectId
from app.classes.user import CreateUserRequest, CreateUserResponse, DeleteUserResponse, GetUserByEmailRequest, GetUserByEmailResponse, GetUserByUsernameRequest, GetUserByUsernameResponse, GetUserByIdResponse, UserInfo
from app.core.database import delete_document, find_documents_with_filters, get_document, insert_document

USER_COLLECTION_NAME = "users"

HASH_ALGORITHM = "pbkdf2_sha256"
HASH_ITERATIONS = 100000


class UserRepository:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance") or cls._instance is None:
            cls._instance = super(UserRepository, cls).__new__(cls)
        return cls._instance

    async def create_user(self, request: CreateUserRequest) -> CreateUserResponse:
        # 1. Generate salt & hash password
        try:
            password_salt = secrets.token_hex(32)  # 32 bytes = 64 hex chars
            hash_algorithm = HASH_ALGORITHM
            password_hash = hashlib.pbkdf2_hmac(
                'sha256',
                request.password.encode('utf-8'),
                password_salt.encode('utf-8'),
                HASH_ITERATIONS 
            ).hex()
        except Exception as e:
            return CreateUserResponse(
                success=False,
                user_id="",
                message="Failed generate password hash"
            )
        
        # 2. Insert user into DB
        user_data = {
            "username": request.username,
            "email": request.email,
            "password_hash": password_hash,
            "password_salt": password_salt,
            "hash_algorithm": hash_algorithm,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "disabled": False
        }

        try:
            user_id = await insert_document(USER_COLLECTION_NAME, user_data)
            if not user_id:
                return CreateUserResponse(
                    success=False,
                    user_id="",
                    message="Failed to insert user"
                )
            
            return CreateUserResponse(
                success=True,
                user_id=user_id,
                message="User created successfully"
            )
        except Exception as e:
            return CreateUserResponse(
                success=False,
                user_id="",
                message="Failed to insert user into DB"
            )

    async def get_user_by_email(self, request: GetUserByEmailRequest) -> GetUserByEmailResponse:
        try:
            # Build filters conditionally
            filters: Dict[str, Any] = {"email": request.email}
            if not request.include_disabled:
                filters["disabled"] = False
            
            users = await find_documents_with_filters(
                USER_COLLECTION_NAME, 
                filters,
                limit=1
            )

            if not users:
                return GetUserByEmailResponse(
                    success=True,
                    user=None,
                    message="User not found"
                )
            
            user = users[0]
            user_info = UserInfo(
                id=str(user["_id"]),
                username=user["username"],
                email=user["email"],
                password_hash=user["password_hash"],
                password_salt=user["password_salt"],
                hash_algorithm=user["hash_algorithm"],
                created_at=user["created_at"],
                updated_at=user["updated_at"],
                disabled=user["disabled"]
            )
            
            return GetUserByEmailResponse(
                success=True,
                user=user_info,
                message=""
            )

        except Exception as e:
            return GetUserByEmailResponse(
                success=False,
                user=None,
                message=f"Failed to get user by email: {e}"
            )

    async def get_user_by_username(self, request: GetUserByUsernameRequest) -> GetUserByUsernameResponse:
        try:
            # Build filters conditionally
            filters: Dict[str, Any] = {"username": request.username}
            if not request.include_disabled:
                filters["disabled"] = False
            
            users = await find_documents_with_filters(
                USER_COLLECTION_NAME, 
                filters,
                limit=1
            )

            if not users:
                return GetUserByUsernameResponse(
                    success=True,
                    user=None,
                    message="User not found"
                )
            
            user = users[0]
            user_info = UserInfo(
                id=str(user["_id"]),
                username=user["username"],
                email=user["email"],
                password_hash=user["password_hash"],
                password_salt=user["password_salt"],
                hash_algorithm=user["hash_algorithm"],
                created_at=user["created_at"],
                updated_at=user["updated_at"],
                disabled=user["disabled"]
            )
            
            return GetUserByUsernameResponse(
                success=True,
                user=user_info,
                message=""
            )

        except Exception as e:
            return GetUserByUsernameResponse(
                success=False,
                user=None,
                message=f"Failed to get user by username: {e}"
            )

    async def get_user_by_id(self, id: str) -> GetUserByIdResponse:
        if not ObjectId.is_valid(id):
            return GetUserByIdResponse(
                success=False,
                user=None,
                status_code=400,
                message="Invalid user ID format"
            )
        
        try:
            user = await get_document(USER_COLLECTION_NAME, id)
            
            if not user:
                return GetUserByIdResponse(
                    success=True,
                    user=None,
                    status_code=404,
                    message="User not found"
                )
            
            user_info = UserInfo(
                id=str(user["_id"]),
                username=user["username"],
                email=user["email"],
                password_hash=user["password_hash"],
                password_salt=user["password_salt"],
                hash_algorithm=user["hash_algorithm"],
                created_at=user["created_at"],
                updated_at=user["updated_at"],
                disabled=user["disabled"]
            )
            
            return GetUserByIdResponse(
                success=True,
                user=user_info,
                status_code=200,
                message=""
            )
        except Exception as e:
            return GetUserByIdResponse(
                success=False,
                user=None,
                status_code=500,
                message=f"Failed to get user by id: {e}"
            )

    async def delete_user(self, id: str) -> DeleteUserResponse:
        if not ObjectId.is_valid(id):
            return DeleteUserResponse(
                success=False,
                message="Invalid user ID format",
                status_code=400
            )
        
        try:
            user = await get_document(USER_COLLECTION_NAME, id)
            if not user:
                return DeleteUserResponse(
                    success=False,
                    message="User not found",
                    status_code=404
                )
            
            user_deleted = await delete_document(USER_COLLECTION_NAME, id)
            if user_deleted:
                return DeleteUserResponse(
                    success=True,
                    message="User deleted successfully",
                    status_code=200
                )
            else:
                return DeleteUserResponse(
                    success=False,
                    message="Failed to delete user",
                    status_code=500
                )
        except Exception as e:
            return DeleteUserResponse(
                success=False,
                message=f"Failed to delete user: {e}",
                status_code=500
            )
from datetime import datetime, timezone
import secrets
import hashlib
from app.classes.user import CreateUserRequest, CreateUserResponse, UserInfo
from app.core.database import insert_document

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
            "updated_at": datetime.now(timezone.utc)
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

        

    async def get_user_by_email(self, email: str) -> UserInfo:
        return UserInfo(
            id="123",
            username="test",
            email="test@test.com",
            password_hash="123",
            password_salt="456",
            hash_algorithm="pbkdf2_sha256",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
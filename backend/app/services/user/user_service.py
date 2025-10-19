import logging
from app.services.user.user_repository import UserRepository
from app.classes.user import CreateUserRequest, GetUserByEmailRequest, RegisterUserRequest, RegisterUserResponse


class UserService:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance") or cls._instance is None:
            cls._instance = super(UserService, cls).__new__(cls)
        return cls._instance

    async def register_user(self, request: RegisterUserRequest) -> RegisterUserResponse:
        # 1. Input validation
        if not request.username or not request.email or not request.password:
            return RegisterUserResponse(
                success=False,
                user_id="",
                status_code=400,
                message="Invalid input"
            )
        
        # 2. Check if user already exists
        get_user_by_email_response = await UserRepository().get_user_by_email(
            GetUserByEmailRequest(email=request.email, include_disabled=False)
        )
        logging.getLogger("uvicorn.error").info(f"get_user_by_email_response: {get_user_by_email_response}")
        if not get_user_by_email_response.success:
            return RegisterUserResponse(
                success=False,
                user_id="",
                status_code=500,
                message="Failed to to check if user already exists"
            )
        if get_user_by_email_response.user:
            return RegisterUserResponse(
                success=False,
                user_id="",
                status_code=400,
                message="User already exists"
            )
        
        # 3. Create user
        create_user_response = await UserRepository().create_user(CreateUserRequest(
            username=request.username,
            email=request.email,
            password=request.password
        ))
        if not create_user_response.success:
            return RegisterUserResponse(
                success=False,
                user_id="",
                status_code=500,
                message="Failed to create user"
            )

        return RegisterUserResponse(
            success=True,
            user_id=create_user_response.user_id,
            status_code=200,
            message="User created successfully"
        )
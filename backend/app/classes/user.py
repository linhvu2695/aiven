from datetime import datetime
from pydantic import BaseModel


class UserInfo(BaseModel):
    id: str
    username: str
    email: str
    password_hash: str
    password_salt: str
    hash_algorithm: str
    created_at: datetime
    updated_at: datetime
    disabled: bool = False

class RegisterUserRequest(BaseModel):
    username: str
    email: str
    password: str

class RegisterUserResponse(BaseModel):
    success: bool
    user_id: str
    status_code: int
    message: str

class CreateUserRequest(BaseModel):
    username: str
    email: str
    password: str

class CreateUserResponse(BaseModel):
    success: bool
    user_id: str
    message: str

class LoginUserRequest(BaseModel):
    email: str
    password: str

class LoginUserResponse(BaseModel):
    success: bool
    user_id: str
    message: str

class GetUserByEmailRequest(BaseModel):
    email: str
    include_disabled: bool = False

class GetUserByEmailResponse(BaseModel):
    success: bool
    user: UserInfo | None
    message: str

class GetUserByUsernameRequest(BaseModel):
    username: str
    include_disabled: bool = False

class GetUserByUsernameResponse(BaseModel):
    success: bool
    user: UserInfo | None
    message: str

class GetUserByIdResponse(BaseModel):
    success: bool
    user: UserInfo | None
    status_code: int
    message: str

class GetUserApiResponse(BaseModel):
    success: bool
    user: dict | None
    status_code: int
    message: str
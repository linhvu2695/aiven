from fastapi import APIRouter, HTTPException

from app.classes.user import GetUserApiResponse, RegisterUserRequest, RegisterUserResponse
from app.services.user.user_service import UserService
from app.services.user.user_repository import UserRepository

router = APIRouter()

@router.post("/register", response_model=RegisterUserResponse)
async def register_user(request: RegisterUserRequest):
    response = await UserService().register_user(request)
    if response.success:
        return response
    else:
        raise HTTPException(status_code=response.status_code, detail=response.message)

@router.get("/{id}", response_model=GetUserApiResponse)
async def get_user(id: str):
    response = await UserRepository().get_user_by_id(id)

    if response.success and response.user:
        # Remove password_hash, password_salt, and hash_algorithm from the response
        user_dict = response.user.model_dump()
        user_dict.pop("password_hash", None)
        user_dict.pop("password_salt", None)
        user_dict.pop("hash_algorithm", None)
        return GetUserApiResponse(
            success=response.success,
            user=user_dict,
            status_code=response.status_code,
            message=response.message
        )
    else:
        raise HTTPException(status_code=response.status_code, detail=response.message)

@router.delete("/{id}")
async def delete_user(id: str):
    response = await UserRepository().delete_user(id)
    if response.success and response.status_code == 200:
        return response
    else:
        raise HTTPException(status_code=response.status_code, detail=response.message)
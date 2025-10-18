from fastapi import APIRouter, HTTPException

from app.classes.user import RegisterUserRequest
from app.services.user.user_service import UserService

router = APIRouter()

@router.post("/register")
async def register_user(request: RegisterUserRequest):
    response = await UserService().register_user(request)
    if response.success:
        return response
    else:
        raise HTTPException(status_code=response.status_code, detail=response.message)
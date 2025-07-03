from fastapi import APIRouter, Response, UploadFile, File, HTTPException
from datetime import timedelta
from app.core.storage import FirebaseStorageRepository

router = APIRouter()

@router.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    try:
        url = await FirebaseStorageRepository().upload(file.file, str(file.filename))
        return {"url": url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/download/{filename}")
async def download_file(filepath: str):
    try:
        content = await FirebaseStorageRepository().download(filepath)
        return Response(content, media_type="application/octet-stream")
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/url/{filepath}")  
async def get_presigned_url(filepath: str, expiration: int = 60):
    try:
        url = await FirebaseStorageRepository().get_presigned_url(filepath, expiration)
        return {"url": url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
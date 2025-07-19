from fastapi import APIRouter, UploadFile, File, HTTPException
import os

router = APIRouter()

@router.post("/upload-bgm")
async def upload_bgm(file: UploadFile = File(...)):
    """
    Upload a BGM file and save it to uploaded_bgm/. Returns the saved filename.
    """
    upload_dir = os.path.join(os.getcwd(), "uploaded_bgm")
    os.makedirs(upload_dir, exist_ok=True)
    file_location = os.path.join(upload_dir, file.filename)
    try:
        with open(file_location, "wb") as f:
            content = await file.read()
            f.write(content)
        return {"filename": file.filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload BGM: {e}")

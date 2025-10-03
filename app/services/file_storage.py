import os
import shutil
import uuid
from fastapi import APIRouter, File, UploadFile, HTTPException, status


MEDIA_DIR = "app/media"
ALLOW_MIME = ["image/png", "image/jpeg"]


def ensure_media_dir() -> None:
    os.makedirs(MEDIA_DIR, exist_ok=True)


def save_uploaded_image(file: UploadFile) -> dict:
    if file.content_type not in ALLOW_MIME:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo se permiten imágenes PNG o JPEG"
        )

    ensure_media_dir()
    ext = os.path.splitext(file.filename)[1]  # .png, .jpeg
    filename = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(MEDIA_DIR, filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "filename": filename,
        "conten_type": file.content_type,
        "url": f"/media/{filename}",
    }

from fastapi import APIRouter, Depends, HTTPException, Body, status, Header, Query
from typing import Optional, List
import json
from Schema.schema import ImageData
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
import base64
from PIL import Image
from io import BytesIO

router = APIRouter(
    prefix="/image",
    tags=["image"],
    responses={404: {"description": "Not found"}},
)

@router.post("/")
async def save_image(data: ImageData = Body(..., description="Image data")):
    base64_data = data.image.replace('data:image/jpeg;base64,', '')
    image_bytes = base64.b64decode(base64_data)

    image = Image.open(BytesIO(image_bytes))

    image_path = "output.jpg"
    image.save(image_path)
    
    return JSONResponse(status_code=status.HTTP_202_ACCEPTED, content={"message": "Image saved successfully.", "image_path": image_path})
from fastapi import APIRouter, Depends, HTTPException, Body, status, Header, Query
from typing import Optional, List
import json
from Schema.schema import ImageData
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

router = APIRouter(
    prefix="/image",
    tags=["image"],
    responses={404: {"description": "Not found"}},
)

@router.post("/get")
async def career_recommend(data: ImageData = Body(..., description="Image data")):
    response = data
    
    return JSONResponse(status_code=status.HTTP_202_ACCEPTED, content=response)
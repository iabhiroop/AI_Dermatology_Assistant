from fastapi import APIRouter, Depends, HTTPException, Body, status, Header, Query
from typing import Optional, List
import json
from Schema.schema import SymptomData
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from connections.mongo_db import db_client

router = APIRouter(
    prefix="/symptoms",
    tags=["symptoms"],
    responses={404: {"description": "Not found"}},
)

@router.post("/")
async def save_symptoms(data: SymptomData = Body(..., description="Image data")):
    response = data
    print(data, type(data))
    return "got it"
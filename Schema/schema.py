from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Union

class ImageData(BaseModel):
    userid: str = Field(..., description="user id")
    image: str = Field(..., description="Base64 encoded image data")
    
class SymptomData(BaseModel):
    userid: str = Field(..., description="user id")
    symptoms: str = Field(..., description="")

class AnalyseData(BaseModel):
    userid: str = Field(..., description="user id")

class InitializeData(BaseModel):
    userid: str = Field(..., description="user id")
    
class ChatData(BaseModel):
    userid: str = Field(..., description="user id")
    query: str = Field(..., description="")
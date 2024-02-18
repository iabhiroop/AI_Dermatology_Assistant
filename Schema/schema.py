from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Union

class ImageData(BaseModel):
    userid: str = Field(..., description="user id")
    image: str = Field(..., description="Base64 encoded image data")
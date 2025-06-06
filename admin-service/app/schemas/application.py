from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ApplicationBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = None
    domain_id: int
    config: Optional[str] = None  # JSON stored as text
    api_key: Optional[str] = None
    is_active: Optional[bool] = True

class ApplicationCreate(ApplicationBase):
    pass

class ApplicationUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = None
    domain_id: Optional[int] = None
    config: Optional[str] = None
    api_key: Optional[str] = None
    is_active: Optional[bool] = None

class ApplicationResponse(ApplicationBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True
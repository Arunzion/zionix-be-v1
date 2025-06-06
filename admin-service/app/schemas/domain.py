from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class DomainBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = None
    config: Optional[str] = None  # JSON stored as text
    is_active: Optional[bool] = True

class DomainCreate(DomainBase):
    pass

class DomainUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = None
    config: Optional[str] = None
    is_active: Optional[bool] = None

class DomainResponse(DomainBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True
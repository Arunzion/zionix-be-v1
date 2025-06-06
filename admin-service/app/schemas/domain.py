from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class DomainBase(BaseModel):
    domain_name: str = Field(..., min_length=3, max_length=100)  # Updated from 'name'
    domain_code: str = Field(..., min_length=3, max_length=50)   # Added 'domain_code'
    description: Optional[str] = None  # Remains unchanged
    status: Optional[bool] = True  # Renamed from 'is_active'
    action: Optional[str] = None  # Added 'action'

class DomainCreate(DomainBase):
    pass  # No changes required

class DomainUpdate(BaseModel):
    domain_name: Optional[str] = Field(None, min_length=3, max_length=100)  # Updated from 'name'
    domain_code: Optional[str] = Field(None, min_length=3, max_length=50)   # Added 'domain_code'
    description: Optional[str] = None
    status: Optional[bool] = None  # Renamed from 'is_active'
    action: Optional[str] = None  # Added 'action'

class DomainResponse(DomainBase):
    id: int  # Remains unchanged
    created_at: datetime  # Remains unchanged
    updated_at: Optional[datetime] = None  # Remains unchanged

    class Config:
        orm_mode = True  # Updated from 'from_attributes' for compatibility with older Pydantic versions

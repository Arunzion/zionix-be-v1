from sqlalchemy import Boolean, Column, Integer, String, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.session import Base

class Domain(Base):
    __tablename__ = "domains"

    id = Column(Integer, primary_key=True, index=True)
    domain_name = Column(String(100), unique=True, index=True, nullable=False)  # Updated from 'name'
    domain_code = Column(String(50), unique=True, index=True, nullable=False)   # Added new field for domain code
    description = Column(Text, nullable=True)  # Remains unchanged
    status = Column(Boolean, default=True)  # Renamed from 'is_active'
    action = Column(Text, nullable=True)  # Added new field for potential actions or configurations
    created_at = Column(DateTime(timezone=True), server_default=func.now())  # Remains unchanged
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())  # Remains unchanged

    # Relationships
    applications = relationship("Application", back_populates="domain", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Domain {self.domain_name}>"

from sqlalchemy import Boolean, Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.session import Base

class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    application_name = Column(String(100), index=True, nullable=False)  # Updated from `name` to `application_name`
    application_code = Column(String(50), unique=True, index=True, nullable=False)  # Added `application_code`
    description = Column(Text, nullable=True)  # Unchanged
    status = Column(Boolean, default=True)  # Renamed from `is_active`
    action = Column(String(50), nullable=True)  # Added `action` field
    domain_name = Column(String(100), ForeignKey("domains.domain_name"), nullable=False)  # Changed `domain_id` to `domain_name`
    config = Column(Text, nullable=True)  # Unchanged
    created_at = Column(DateTime(timezone=True), server_default=func.now())  # Unchanged
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())  # Unchanged

    # Relationships
    domain = relationship("Domain", back_populates="applications")  # Unchanged

    def __repr__(self):
        return f"<Application {self.application_name}>"

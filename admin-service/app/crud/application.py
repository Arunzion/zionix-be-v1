from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import List, Optional

from app.models.application import Application
from app.schemas.application import ApplicationCreate, ApplicationUpdate
from app.crud.domain import get_domain

def get_application(db: Session, application_id: int) -> Optional[Application]:
    """Get an application by ID"""
    return db.query(Application).filter(Application.id == application_id).first()

def get_application_by_name_and_domain(db: Session, name: str, domain_id: int) -> Optional[Application]:
    """Get an application by name and domain ID"""
    return db.query(Application).filter(Application.name == name, Application.domain_id == domain_id).first()

def get_applications(db: Session, skip: int = 0, limit: int = 100) -> List[Application]:
    """Get all applications with pagination"""
    return db.query(Application).offset(skip).limit(limit).all()

def get_applications_by_domain(db: Session, domain_id: int, skip: int = 0, limit: int = 100) -> List[Application]:
    """Get all applications for a specific domain with pagination"""
    return db.query(Application).filter(Application.domain_id == domain_id).offset(skip).limit(limit).all()

def create_application(db: Session, application: ApplicationCreate) -> Application:
    """Create a new application"""
    # Check if domain exists
    domain = get_domain(db, domain_id=application.domain_id)
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")
    
    # Check if application name already exists in this domain
    db_application = get_application_by_name_and_domain(db, name=application.name, domain_id=application.domain_id)
    if db_application:
        raise HTTPException(status_code=400, detail="Application name already exists in this domain")
    
    # Create new application
    db_application = Application(
        name=application.name,
        description=application.description,
        domain_id=application.domain_id,
        config=application.config,
        api_key=application.api_key,
        is_active=application.is_active
    )
    db.add(db_application)
    db.commit()
    db.refresh(db_application)
    return db_application

def update_application(db: Session, application_id: int, application: ApplicationUpdate) -> Application:
    """Update an application"""
    db_application = get_application(db, application_id=application_id)
    if not db_application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    update_data = application.dict(exclude_unset=True)
    
    # Check domain exists if being updated
    if "domain_id" in update_data:
        domain = get_domain(db, domain_id=update_data["domain_id"])
        if not domain:
            raise HTTPException(status_code=404, detail="Domain not found")
    
    # Check name uniqueness if being updated
    if "name" in update_data and update_data["name"] != db_application.name:
        domain_id = update_data.get("domain_id", db_application.domain_id)
        if get_application_by_name_and_domain(db, name=update_data["name"], domain_id=domain_id):
            raise HTTPException(status_code=400, detail="Application name already exists in this domain")
    
    for key, value in update_data.items():
        setattr(db_application, key, value)
    
    db.add(db_application)
    db.commit()
    db.refresh(db_application)
    return db_application

def delete_application(db: Session, application_id: int) -> None:
    """Delete an application"""
    db_application = get_application(db, application_id=application_id)
    if not db_application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    db.delete(db_application)
    db.commit()
    return None
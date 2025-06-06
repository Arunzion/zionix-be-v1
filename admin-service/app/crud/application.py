from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import List, Optional

from app.models.application import Application
from app.schemas.application import ApplicationCreate, ApplicationUpdate
from app.crud.domain import get_domain_by_name

def get_application(db: Session, application_id: int) -> Optional[Application]:
    """Get an application by ID"""
    return db.query(Application).filter(Application.id == application_id).first()

def get_all_applications(db: Session, skip: int = 0, limit: int = 100) -> List[Application]:
    """Get all applications with pagination"""
    return db.query(Application).offset(skip).limit(limit).all()

def fetch_applications_by_domain_name(
    db: Session, domain_name: str, application_name: Optional[str] = None, skip: int = 0, limit: int = 100
) -> List[Application]:
    """
    Fetch applications by domain name with optional filtering by application name.
    Supports pagination.
    """
    query = db.query(Application).filter(Application.domain_name == domain_name)
    if application_name:
        query = query.filter(Application.application_name == application_name)
    return query.offset(skip).limit(limit).all()





def create_application(db: Session, application: ApplicationCreate) -> Application:
    """Create a new application"""
    # Check if domain exists
    domain = get_domain_by_name(db, domain_name=application.domain_name)
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")

    # Check if application name already exists in this domain
    existing_applications = fetch_applications_by_domain_name(
        db, domain_name=application.domain_name
    )
    if any(app.application_name == application.application_name for app in existing_applications):
        raise HTTPException(status_code=400, detail="Application name already exists in this domain")

    # Create new application
    db_application = Application(
        application_name=application.application_name,
        application_code=application.application_code,
        description=application.description,
        domain_name=application.domain_name,
        config=application.config,
        status=application.status,
        action=application.action,
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
    
    # Check if the domain exists when being updated
    if "domain_name" in update_data:
        domain = get_domain_by_name(db, domain_name=update_data["domain_name"])
        if not domain:
            raise HTTPException(status_code=404, detail="Domain not found")
    
    # Check for unique application name within the domain if being updated
    if "application_name" in update_data and update_data["application_name"] != db_application.application_name:
        domain_name = update_data.get("domain_name", db_application.domain_name)
        if fetch_applications_by_domain_name(
            db, domain_name=domain_name, application_name=update_data["application_name"]
        ):
            raise HTTPException(status_code=400, detail="Application name already exists in this domain")
    
    # Update the application fields
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

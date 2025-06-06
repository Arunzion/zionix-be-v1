from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.session import get_db
from app.schemas.application import ApplicationCreate, ApplicationUpdate, ApplicationResponse
from app.crud.application import create_application, get_application, get_applications, update_application, delete_application

router = APIRouter(prefix="/applications", tags=["applications"])

@router.post("/", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
async def create_new_application(application: ApplicationCreate, db: Session = Depends(get_db)):
    """Create a new application"""
    db_application = create_application(db=db, application=application)
    return db_application

@router.get("/{application_id}", response_model=ApplicationResponse)
async def read_application(application_id: int, db: Session = Depends(get_db)):
    """Get application by ID"""
    db_application = get_application(db=db, application_id=application_id)
    if db_application is None:
        raise HTTPException(status_code=404, detail="Application not found")
    return db_application

@router.get("/", response_model=List[ApplicationResponse])
async def read_applications(skip: int = 0, limit: int = 100, domain_id: Optional[int] = None, db: Session = Depends(get_db)):
    """Get all applications with optional domain filter and pagination"""
    applications = get_applications(db=db, skip=skip, limit=limit, domain_id=domain_id)
    return applications

@router.put("/{application_id}", response_model=ApplicationResponse)
async def update_existing_application(application_id: int, application: ApplicationUpdate, db: Session = Depends(get_db)):
    """Update an application"""
    db_application = get_application(db=db, application_id=application_id)
    if db_application is None:
        raise HTTPException(status_code=404, detail="Application not found")
    updated_application = update_application(db=db, application_id=application_id, application=application)
    return updated_application

@router.delete("/{application_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_existing_application(application_id: int, db: Session = Depends(get_db)):
    """Delete an application"""
    db_application = get_application(db=db, application_id=application_id)
    if db_application is None:
        raise HTTPException(status_code=404, detail="Application not found")
    delete_application(db=db, application_id=application_id)
    return None
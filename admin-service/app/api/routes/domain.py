from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.schemas.domain import DomainCreate, DomainUpdate, DomainResponse
from app.crud.domain import create_domain, get_domain, get_domains, update_domain, delete_domain
from app.events.producers.domain_created import publish_domain_created_event

router = APIRouter(prefix="/domains", tags=["domains"])

@router.post("/create_domain/", response_model=DomainResponse, status_code=status.HTTP_201_CREATED)
async def create_new_domain(domain: DomainCreate, db: Session = Depends(get_db)):
    """Create a new domain"""
    db_domain = create_domain(db=db, domain=domain)
    # Publish domain created event
    await publish_domain_created_event(domain_id=db_domain.id, domain_name=db_domain.domain_name)
    return db_domain

@router.get("/get_domain/{domain_id}", response_model=DomainResponse)
async def read_domain(domain_id: int, db: Session = Depends(get_db)):
    """Get domain by ID"""
    db_domain = get_domain(db=db, domain_id=domain_id)
    if db_domain is None:
        raise HTTPException(status_code=404, detail="Domain not found")
    return db_domain

@router.get("/get_all_domains/", response_model=List[DomainResponse])
async def read_domains(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all domains with pagination"""
    domains = get_domains(db=db, skip=skip, limit=limit)
    return domains

@router.put("/update_domain/{domain_id}", response_model=DomainResponse)
async def update_existing_domain(domain_id: int, domain: DomainUpdate, db: Session = Depends(get_db)):
    """Update a domain"""
    db_domain = get_domain(db=db, domain_id=domain_id)
    if db_domain is None:
        raise HTTPException(status_code=404, detail="Domain not found")
    updated_domain = update_domain(db=db, domain_id=domain_id, domain=domain)
    return updated_domain

@router.delete("/delete_domain/{domain_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_existing_domain(domain_id: int, db: Session = Depends(get_db)):
    """Delete a domain"""
    db_domain = get_domain(db=db, domain_id=domain_id)
    if db_domain is None:
        raise HTTPException(status_code=404, detail="Domain not found")
    delete_domain(db=db, domain_id=domain_id)
    return None

from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import List, Optional

from app.models.domain import Domain
from app.schemas.domain import DomainCreate, DomainUpdate

def get_domain(db: Session, domain_id: int) -> Optional[Domain]:
    """Get a domain by ID"""
    return db.query(Domain).filter(Domain.id == domain_id).first()

def get_domain_by_name(db: Session, name: str) -> Optional[Domain]:
    """Get a domain by name"""
    return db.query(Domain).filter(Domain.name == name).first()

def get_domains(db: Session, skip: int = 0, limit: int = 100) -> List[Domain]:
    """Get all domains with pagination"""
    return db.query(Domain).offset(skip).limit(limit).all()

def create_domain(db: Session, domain: DomainCreate) -> Domain:
    """Create a new domain"""
    # Check if domain name already exists
    db_domain = get_domain_by_name(db, name=domain.name)
    if db_domain:
        raise HTTPException(status_code=400, detail="Domain name already registered")
    
    # Create new domain
    db_domain = Domain(
        name=domain.name,
        description=domain.description,
        config=domain.config,
        is_active=domain.is_active
    )
    db.add(db_domain)
    db.commit()
    db.refresh(db_domain)
    return db_domain

def update_domain(db: Session, domain_id: int, domain: DomainUpdate) -> Domain:
    """Update a domain"""
    db_domain = get_domain(db, domain_id=domain_id)
    if not db_domain:
        raise HTTPException(status_code=404, detail="Domain not found")
    
    update_data = domain.dict(exclude_unset=True)
    
    # Check name uniqueness if being updated
    if "name" in update_data and update_data["name"] != db_domain.name:
        if get_domain_by_name(db, name=update_data["name"]):
            raise HTTPException(status_code=400, detail="Domain name already registered")
    
    for key, value in update_data.items():
        setattr(db_domain, key, value)
    
    db.add(db_domain)
    db.commit()
    db.refresh(db_domain)
    return db_domain

def delete_domain(db: Session, domain_id: int) -> None:
    """Delete a domain"""
    db_domain = get_domain(db, domain_id=domain_id)
    if not db_domain:
        raise HTTPException(status_code=404, detail="Domain not found")
    
    db.delete(db_domain)
    db.commit()
    return None
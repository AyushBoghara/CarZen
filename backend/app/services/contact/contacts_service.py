from datetime import datetime, timezone

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.users import User
from app.models.contact import Contact
from app.services.address import address_service
from app.models.address import Address

def create_contact(db:Session,owner:User,value:dict) -> Contact:
    if owner is None or owner.id is None:
        raise PermissionError(
            "Authenticated user not found."
        )
        
    address_id = value.get("address_id")

    if address_id is None:
        raise ValueError("Address ID is required.")
    
    address = address_service.get_address_by_id(db,address_id,owner)
    
    if address is None:
        raise LookupError("Address Not Found.")

    contact = Contact(user_id=owner.id,**value)
    db.add(contact)
    
    try:
        db.commit()
        db.refresh(contact)
    except IntegrityError as e:
        db.rollback()
        raise ValueError(
            "Unable to create Contact. Please check the contact data."
        ) from e
    return contact

def get_all_contact(db:Session,owner:User)->Contact:
    qurey = db.query(Contact).filter(Contact.user_id == owner.id,Contact.deleted_at.is_(None)).all()
    return qurey

def get_contact_by_id(db:Session,owner:User,contact_id:int)->Contact:
    qurey = db.query(Contact).filter(
        Contact.id == contact_id,
        Contact.user_id == owner.id,
        Contact.deleted_at.is_(None)
    ).first()
    return qurey

def update_contact(db:Session,owner:User,contact_id:int,value:dict):
    contact = get_contact_by_id(db,owner,contact_id)
    
    if contact is None:
        raise LookupError("Contact Not Found.")
    
    update_data = {
        key:val for key,val in value.items()
        if val is not None
    }
    if "address_id" in update_data:

        address = (
            db.query(Address)
            .filter(
                Address.id == update_data["address_id"],
                Address.user_id == owner.id,
                Address.deleted_at.is_(None)
            )
            .first()
        )

        if address is None:
            raise LookupError("Address Not Found.")

    
    for key,val in update_data.items():
        setattr(contact,key,val)
        
    db.commit()
    db.refresh(contact)
    
    return contact

def delete_contact(db:Session,contact_id:int,owner:User)->None:
    contact = get_contact_by_id(db,owner,contact_id)
    if contact is None:
        raise LookupError("Contact Not Found.")
    
    contact.deleted_at = datetime.now(timezone.utc)
    db.commit()

def update_contact_visibility(
    db: Session,
    owner: User,
    contact_id: int,
    value: dict
) -> Contact:

    contact = get_contact_by_id(
        db,
        owner,
        contact_id
    )

    if contact is None:
        raise LookupError("Contact Not Found.")

    contact.contact_visibility = value["contact_visibility"]

    try:
        db.commit()
        db.refresh(contact)

    except IntegrityError as e:
        db.rollback()
        raise ValueError(
            "Unable to update contact visibility."
        ) from e

    return contact
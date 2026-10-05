from datetime import datetime, timezone

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.users import User
from app.models.address import Address

def create_address(db: Session,owner:User,value:dict) -> Address:
   
    if owner is None or owner.id is None:
        raise PermissionError(
            "Authenticated user not found."
        )
    # Never allow user_id from request data
    value.pop("user_id", None)

    if value.get("is_default") is True:

        db.query(Address).filter(
            Address.user_id == owner.id,
            Address.deleted_at.is_(None),
            Address.is_default.is_(True)
        ).update(
            {
                Address.is_default: False
            },
            synchronize_session=False
        )
        
    address = Address(user_id=owner.id, **value)
    db.add(address)
    
    try:
        db.commit()
        db.refresh(address)
    except IntegrityError as e:
        db.rollback()
        raise ValueError(
            "Unable to create address. Please check the address data."
        ) from e    
        
    return address

def get_addresses(
    db: Session,
    owner: User
) -> Address:

    query = (
        db.query(Address)
            .filter(
                Address.user_id == owner.id,
                Address.deleted_at.is_(None)
            )
            .order_by(Address.is_default.desc(), Address.id.desc()).all()
        )
    
    return query

def get_address_by_id(db: Session,address_id: int,owner: User) -> Address :
    query = db.query(Address).filter(Address.id == address_id,Address.user_id == owner.id,Address.deleted_at.is_(None)).first()
    return query 

def update_address(db:Session,address_id:int,owner:User,value:dict):
    address = get_address_by_id(db,owner,address_id)
    
    if address is None:
       raise LookupError("Address Not Found.")
    
    update_data = {
        key:val 
        for key,val in value.items()
        if val is not None
    }
    # If this address is being made default,
    # remove default from other addresses.
    if update_data.get("is_default") is True:

        db.query(Address).filter(
            Address.user_id == owner.id,
            Address.id != address_id,
            Address.deleted_at.is_(None),
            Address.is_default.is_(True)
        ).update(
            {
                Address.is_default: False
            },
            synchronize_session=False
        )
        
    for key,val in update_data.items():
        setattr(address,key,val)
        
    db.commit()
    db.refresh(address)

    return address

def delete_address(db:Session,address_id:int,owner:User) ->None:
    address = get_address_by_id(db, address_id, owner)
    if address is None:
        raise LookupError("Address not found.")

    address.deleted_at = datetime.now(timezone.utc)
    db.commit()

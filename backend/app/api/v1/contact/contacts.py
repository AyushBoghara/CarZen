
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth_dependencies import get_current_user
from app.database.connection.conn import get_db
from app.models.users import User
from app.schemas.users_schema import MessageResponse
from app.schemas.contact_schema import ContactCreate,ContactUpdate,ContactVisibilityUpdate,SellerContactResponse
from app.services.contact import contacts_service
router = APIRouter()

def _raise(exc: Exception):
    if isinstance(exc, LookupError) and "not among the defined enum values" not in str(exc):
        code = status.HTTP_404_NOT_FOUND
    elif isinstance(exc, PermissionError): 
        code = status.HTTP_403_FORBIDDEN
    elif isinstance(exc, ValueError): 
        code = status.HTTP_409_CONFLICT
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{type(exc).__name__}: {str(exc)}",
            ) from exc
    raise HTTPException(code, str(exc)) from exc


@router.post("/contact-add",response_model=SellerContactResponse,status_code=201)
def create_contact(
    payload:ContactCreate,
    db:Session = Depends(get_db),
    current_user:User=Depends(get_current_user)
):
    try:
        return contacts_service.create_contact(db,current_user,payload.model_dump())
    except Exception as e:
        _raise(e)
        
@router.get("/contact",response_model=list[SellerContactResponse])
def get_contact(
    db:Session = Depends(get_db),
    current_user:User=Depends(get_current_user)
):
    try:
        return contacts_service.get_all_contact(db,current_user)
    except Exception as e:
        _raise(e)
        
@router.get("/contact/{contact_id}",response_model=SellerContactResponse)
def get_contact_by_id(
    contact_id:int,
    db:Session = Depends(get_db),
    current_user:User=Depends(get_current_user)
):
    try:
        contact = contacts_service.get_contact_by_id(db,current_user,contact_id)
        if contact is None:
            raise HTTPException(
                status_code=404,detail="Contact Not Found."
            )
        return contact
    except Exception as e:
        _raise(e)
      
@router.patch("/contact/{contact_id}",response_model=SellerContactResponse)  
def update_contact(
    contact_id:int,
    payload: ContactUpdate,
    db:Session = Depends(get_db),
    current_user:User = Depends(get_current_user)
):
    try:
        return contacts_service.update_contact(db,current_user,contact_id,payload.model_dump(exclude_unset=True))
    except Exception as e:
        _raise(e)
        

@router.delete("/contact/{contact_id}",response_model=MessageResponse)
def delete_contact(
    contact_id:int,
    db:Session = Depends(get_db),
    current_user:User = Depends(get_current_user)
):
    try:
        contacts_service.delete_contact(db,contact_id,current_user)
        return {"message": "Contact deleted successfully."}
    except Exception as e:
        _raise(e)
        
@router.patch("/contact/{contact_id}/visibility", response_model=SellerContactResponse)
def contact_visibility_update(
    contact_id: int,
    payload: ContactVisibilityUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        return contacts_service.update_contact_visibility(
            db,current_user,contact_id,payload.model_dump()
        )

    except Exception as exc:
        _raise(exc)
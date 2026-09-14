
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth_dependencies import get_current_user
from app.database.connection.conn import get_db
from app.models.users import User
from app.schemas.address_schema import AddressCreate,AddressUpdate,AddressResponse
from app.services.address import address_service
from app.schemas.users_schema import MessageResponse

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

@router.post("/address-add",response_model=AddressResponse,status_code=201)
def create_address(
    payload:AddressCreate,
    db: Session = Depends(get_db),
    current_user:User=Depends(get_current_user)
):
    try:
        return address_service.create_address(db,current_user, payload.model_dump())
    except Exception as e:
        _raise(e)

@router.get("/address",response_model=list[AddressResponse])
def get_address(
    db: Session = Depends(get_db),
    current_user:User=Depends(get_current_user)
):
    try:
        address =  address_service.get_addresses(db,current_user)
        if address is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Address not found .")
        return address 
    except Exception as e:
        _raise(e)
    

@router.get("/address/{address_id}",response_model=AddressResponse)
def get_address_by_id(
    address_id:int,
    db: Session = Depends(get_db),
    current_user:User=Depends(get_current_user)
):
    try:
        address =  address_service.get_address_by_id(db,address_id,current_user)
        
        if address is None:
            raise HTTPException(
                status_code=404,
                detail="Address not found."
            )
        return address 
    
    except Exception as e:
        _raise(e)

@router.patch("/address/{address_id}",response_model=AddressResponse)
def update_address(address_id:int,payload:AddressUpdate,db:Session = Depends(get_db),current_user:User = Depends(get_current_user)):
    try:
        return address_service.update_address(db,address_id,current_user,payload.model_dump(exclude_unset=True))
    except Exception as e:
        _raise(e)
        
        
@router.delete("/address/{address_id}",response_model=MessageResponse)
def delete_address(address_id:int,db:Session = Depends(get_db),current_user:User = Depends(get_current_user)):
    try: 
        address_service.delete_address(db, address_id,current_user); 
        return {"message": "Address deleted successfully."}
    except Exception as exc:
        _raise(exc)
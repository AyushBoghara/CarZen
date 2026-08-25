
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.core.auth_dependencies import get_current_user
from app.database.connection.conn import get_db
from app.exceptions.authExceptions import AuthError
from app.models.users import User
from app.schemas.users_schema import (
    Token,
    TokenValidationResponse,
    UserLogin,
    UserRegister,
    UserResponse,
)
from app.services.auth import auth_service

router = APIRouter()

@router.post("/register",response_model=UserResponse,status_code=status.HTTP_201_CREATED)
def register(user:UserRegister,db:Session= Depends(get_db)):
    try:
        return auth_service.register_user(db,user)
    except AuthError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=str(e))
    except IntegrityError:
        # Safety net if service didn't convert the DB error
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username or email already exists.")
    except Exception:
        # Final safety net to avoid leaking internals
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error") 
    
# admin registers 
@router.post("/register-admin",response_model=UserResponse,status_code=status.HTTP_201_CREATED)
def register(user:UserRegister,db:Session= Depends(get_db)):
    try:
        return auth_service.register_admin(db,user)
    except AuthError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=str(e))
    except IntegrityError:
        # Safety net if service didn't convert the DB error
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username or email already exists.")
    except Exception:
        # Final safety net to avoid leaking internals
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error") 
    
    
@router.post("/login",response_model=Token)
def login(user:UserLogin,db:Session = Depends(get_db)):
    try:
        return auth_service.login(db,user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail=str(e))
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")


@router.get("/validate", response_model=TokenValidationResponse)
def validate_access_token(current_user: User = Depends(get_current_user)):
    return {"valid": True, "user": current_user}

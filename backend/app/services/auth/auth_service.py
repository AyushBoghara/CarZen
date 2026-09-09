
from datetime import datetime, timezone

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
import re

from app.core.security import hash_password,verify_password,create_access_token
from app.exceptions.authExceptions import UserAlreadyExistsError,UserNameAlreadyExistsError,WeakPasswordError
from app.models.enums.UserRoles import UserRoles
from app.models.enums.UserStatus import UserStatus
from app.models.users import User
from app.schemas.users_schema import (
    UserRegister,
    UserLogin,
    Token
)


def register_user(db:Session,user:UserRegister):
    if user.role == UserRoles.ADMIN:
        raise ValueError("Admin accounts cannot be self-registered.")

    if user.status != UserStatus.ACTIVE:
        raise ValueError("Account status is assigned automatically during registration.")

    # Check for existing email
    existing_email = (
        db.query(User)
        .filter(User.email == str(user.email))
        .first()
    )    
    if existing_email:
        raise UserAlreadyExistsError("Email already registered. Please log in or use a different email.")

    existing_username = (
        db.query(User)
        .filter(User.username == user.username)
        .first()
    )
    if existing_username:
        raise UserNameAlreadyExistsError("This username is already taken. Please try another or log in.")

    # hash password in user for security purpose 
    try:
        is_valid = is_password_valid(user.password)
        if is_valid == True:
            hashed_password = hash_password(user.password)
    except WeakPasswordError as error:
        raise WeakPasswordError(f"Registration Failed: {error}")

   
    now = datetime.now(timezone.utc)

    # store data in database 
    db_user = User(
        first_name = user.first_name,
        last_name=user.last_name,
        username=user.username,
        email=user.email,
        password=hashed_password,
        phone_number=user.phone_number,
        role=user.role,
        status=UserStatus.ACTIVE,
        profile_image_url = user.profile_image_url
    )
    db.add(db_user)
    try:
        db.commit()
        db.refresh(db_user)
    except IntegrityError as e:
        db.rollback()
        raise ValueError("Failed to register user due to duplicate username or email.") from e
    
    return db_user

# admin register
def register_admin(db:Session,user:UserRegister):
    if user.status != UserStatus.ACTIVE:
        raise ValueError("Account status is assigned automatically during registration.")

    # Check for existing email
    existing_email = (
        db.query(User)
        .filter(User.email == str(user.email))
        .first()
    )    
    if existing_email:
        raise UserAlreadyExistsError("Email already registered. Please log in or use a different email.")

    existing_username = (
        db.query(User)
        .filter(User.username == user.username)
        .first()
    )
    if existing_username:
        raise UserNameAlreadyExistsError("This username is already taken. Please try another or log in.")

    # hash password in user for security purpose 
    try:
        is_valid = is_password_valid(user.password)
        if is_valid == True:
            hashed_password = hash_password(user.password)
    except WeakPasswordError as error:
        raise WeakPasswordError(f"Registration Failed: {error}")

   
    now = datetime.now(timezone.utc)

    # store data in database 
    db_user = User(
        first_name = user.first_name,
        last_name=user.last_name,
        username=user.username,
        email=user.email,
        password=hashed_password,
        phone_number=user.phone_number,
        role= UserRoles.ADMIN,
        status=UserStatus.ACTIVE,
        profile_image_url = user.profile_image_url
    )
    db.add(db_user)
    try:
        db.commit()
        db.refresh(db_user)
    except IntegrityError as e:
        db.rollback()
        raise ValueError("Failed to register user due to duplicate username or email.") from e
    
    return db_user


def login(db:Session,user:UserLogin):
    
    db_user = db.query(User).filter(User.email == user.email).first()
    
    if not db_user or not verify_password(user.password, db_user.password):
        raise ValueError("Invalid email or password.")

    if db_user.deleted_at is not None:
        raise ValueError("This account has been deleted.")

    if db_user.status != UserStatus.ACTIVE:
        raise ValueError("This account is not active.")
    
    token = create_access_token(
        {
            "sub": db_user.email,
            "user_id": db_user.id,
            "role": db_user.role.value,
        }
    )
    
    return {"access_token":token,"token_type":"bearer"}

def is_password_valid(password):
    if len(password) < 8:
        raise WeakPasswordError("Password is too short. It must be at least 8 characters long.")
        
    if not re.search(r"[A-Z]", password):
        raise WeakPasswordError("Password must contain at least one uppercase letter (A-Z).")
        
    if not re.search(r"[a-z]", password):
        raise WeakPasswordError("Password must contain at least one lowercase letter (a-z).")

    if not re.search(r"\d", password):
        raise WeakPasswordError("Password must contain at least one number (0-9).")
        
    if not re.search(r"[\W_]", password):
        raise WeakPasswordError("Password must contain at least one special character (e.g., !, @, #, $, %).")
        
    return True

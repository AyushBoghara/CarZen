from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr

from app.models.enums.UserRoles import UserRoles
from app.models.enums.UserStatus import UserStatus


class UserCreate(BaseModel):
    first_name: str
    last_name: str | None = None
    username: str
    email: EmailStr
    password: str
    phone_number: str | None = None
    role: UserRoles = UserRoles.USER
    status: UserStatus = UserStatus.ACTIVE
    profile_image_url: str | None = None


class UserRegister(BaseModel):
    first_name: str
    last_name: str | None = None
    username: str
    email: EmailStr
    password: str
    phone_number: str | None = None
    role: UserRoles = UserRoles.USER
    status: UserStatus = UserStatus.ACTIVE 
    profile_image_url: str | None = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    first_name: str
    last_name: str | None = None
    username: str
    email: EmailStr
    phone_number: str | None = None
    role: UserRoles
    status: UserStatus
    profile_image_url: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    deleted_at: datetime | None = None

    model_config = ConfigDict(
        from_attributes=True
    )


class Token(BaseModel):
    access_token: str
    token_type: str


class UserUpdateProfile(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    username: str | None = None
    email: EmailStr | None = None
    phone_number: str | None = None
    profile_image_url: str | None = None


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


class UserRoleStatusUpdate(BaseModel):
    role: UserRoles | None = None
    status: UserStatus | None = None


class TokenValidationResponse(BaseModel):
    valid: bool
    user: UserResponse


class MessageResponse(BaseModel):
    message: str

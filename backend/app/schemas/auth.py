from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    full_name: str
    username: str


class UserCreate(BaseModel):
    username: str
    full_name: str
    email: EmailStr
    password: str
    role: str
    department_id: int | None = None


class UserOut(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    username: str
    full_name: str
    email: str
    role: str
    department_id: int | None
    is_active: bool

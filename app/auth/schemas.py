from pydantic import BaseModel, EmailStr

#datos de registro
class RegisterRequest(BaseModel):
    nombre: str
    email: EmailStr
    password: str

#datos de login
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

#esquema para presentar roles
class RolInfo(BaseModel):
    id: int
    codigo: str
    nombre: str

#define como se devuelve un usuario en el frontend
class UserResponse(BaseModel):
    id: int
    nombre: str
    email: str
    roles: list[RolInfo] = []
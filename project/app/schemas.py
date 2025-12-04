from pydantic import BaseModel,EmailStr, Field
from pydantic.types import Annotated
from datetime import datetime
from typing import Optional

class SpecializationResponse(BaseModel):

    name: str
    id: int
    class Config:
        from_attributes = True

class DoctorResponse(BaseModel):
    first_name: str
    last_name: str
    patronymic: str
    specialization: SpecializationResponse

    class Config: 
        from_attributes = True

class DoctorCreate(BaseModel):
    first_name: str
    last_name: str
    patronymic: str
    phone_number: str
    email: EmailStr
    password: str
    specialization_id: int

class SpecializationCreate(BaseModel):
    name: str
    description: Optional[str] = None
from pydantic import BaseModel,EmailStr, Field, field_validator
from pydantic.types import Annotated
from datetime import date, time, datetime
from typing import Optional

class PatientCreate(BaseModel):
    first_name: str
    last_name: str
    patronymic: str
    gender: str
    passport_number: str
    insurance_number: str
    birth_date: date
    phone_number: str
    email: EmailStr
    password: str

class PatientResponse(BaseModel):
    first_name: str
    last_name: str
    patronymic: str
    gender: str
    birth_date: date
    phone_number: str
    email: EmailStr

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

class ScheduleResponse(BaseModel):
    id: int
    office_number: str
    date : date
    start_time: time
    end_time: time
    doctor: DoctorResponse

class ScheduleCreate(BaseModel):
    office_number: str
    date : date
    start_time: time
    end_time: time
    is_available: bool
    doctor_id: int

class ScheduleBatchCreate(BaseModel):
    doctor_id: int
    date: date
    start_time: time
    end_time: time
    slots_count: int
    office_number: str = None
    
    class Config:
        from_attributes = True


class AppointmentCreate(BaseModel):
    schedule_id: int

class AppointmentResponseToPatient(BaseModel):
    schedule: ScheduleResponse

class AppointmentResponse(BaseModel):
    schedule: ScheduleResponse
    patient: PatientResponse
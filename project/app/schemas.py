from pydantic import BaseModel,EmailStr, Field, field_validator
from pydantic.types import Annotated
from datetime import date, time, datetime
from typing import Optional, List

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
    id: int

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
    id: int
    status: str

class AppointmentResponse(BaseModel):
    schedule: ScheduleResponse
    patient: PatientResponse
    information: str
    status: str
    id: int

class MedicamentContradictionsRequest(BaseModel):
    medicament_name: str
    contradictions: List[str]

class MedicamentContradictionRequest(BaseModel):
    medicament_name: str
    contradictions: str

class AppointmentUpdate(BaseModel):
    information: Optional[str] = None
    status: Optional[str] = None
    
    @field_validator('status')
    def validate_status(cls, v):
        if v is not None and v not in ['scheduled', 'completed', 'cancelled', 'no-show']:
            raise ValueError('Недопустимый статус')
        return v
    
class PatientMedicamentBase(BaseModel):
    medicament_name: str
    dosage: Optional[str] = None
    frequency: Optional[str] = None
    start_date: Optional[date] = Field(default_factory=lambda: date.today())
    end_date: Optional[date] = None
    prescribed_by: Optional[str] = None
    notes: Optional[str] = None

class PatientMedicamentCreate(PatientMedicamentBase):
    pass

class PatientMedicamentResponse(PatientMedicamentBase):
    id: int
    patient_id: int
    
    class Config:
        from_attributes = True

class MedicamentsForAppointmentRequest(BaseModel):
    medicaments: List[PatientMedicamentCreate]

    @field_validator('medicaments')
    def validate_medicaments(cls, v):
        if not v:
            raise ValueError('Список лекарств не может быть пустым')
        return v
    
class PatientMedicamentResponse(BaseModel):
    id: int
    patient_id: int
    medicament_name: str
    dosage: Optional[str] = None
    frequency: Optional[str] = None
    start_date: date
    end_date: Optional[date] = None
    prescribed_by: Optional[str] = None
    notes: Optional[str] = None
    
    class Config:
        from_attributes = True

class MedicamentConflictResponse(BaseModel):
    """Модель для конфликтного лекарства"""
    medicament_name: str
    conflict_reasons: List[str]
    
class MedicamentsAppointmentResponse(BaseModel):
    """Модель ответа при назначении лекарств"""
    added_medicaments: List[PatientMedicamentResponse]
    conflicts: List[MedicamentConflictResponse] = []
    warning: Optional[str] = None
    message: Optional[str] = None
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    user_type: str  # 'patient' или 'doctor'

class TokenData(BaseModel):
    id: Optional[str] = None
    user_type: Optional[str] = None

class UserLogin(BaseModel):
    email: str
    password: str
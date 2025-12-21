from pydantic import BaseModel,EmailStr, Field, field_validator, constr
from pydantic.types import Annotated
from datetime import date, time, datetime
from typing import Optional, List

from enum import Enum

class GenderEnum(str,Enum):
    female="female"
    male="male"


class PatientCreate(BaseModel):
    first_name: Annotated[str,Field(min_length=1,max_length=50)]
    last_name: Annotated[str,Field(min_length=1,max_length=50)]
    patronymic: Annotated[str,Field(min_length=1,max_length=50)]
    gender: GenderEnum
    passport_number: Annotated[str,Field(pattern=r'^[0-9]{10,20}$')]
    insurance_number: Annotated[str,Field(pattern=r'^[0-9]{10,35}$')]
    birth_date: date
    phone_number: Annotated[str,Field(pattern=r'^[0-9]{10,15}$')]
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
    description: Optional[str] = None 
    class Config:
        from_attributes = True

class OfficeCreate(BaseModel):
    number: str = Field(..., min_length=1, max_length=15, description="Номер офиса/кабинета")

class OfficeResponse(BaseModel):
    id: int
    number: str
    
    class Config:
        from_attributes = True

class DoctorResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    patronymic: str
    specialization: SpecializationResponse

    class Config: 
        from_attributes = True

class DoctorResponseAdmin(BaseModel):
    id: int
    first_name: str
    last_name: str
    patronymic: str
    email: str
    phone_number: str
    specialization: SpecializationResponse

    class Config: 
        from_attributes = True



class DoctorCreate(BaseModel):
    first_name: Annotated[str,Field(min_length=1,max_length=50)]
    last_name: Annotated[str,Field(min_length=1,max_length=50)]
    patronymic: Annotated[str,Field(min_length=1,max_length=50)]
    phone_number: Annotated[str,Field(pattern=r'^[0-9]{10,15}$')]
    email: EmailStr
    password: str
    specialization_id: int

class SpecializationCreate(BaseModel):
    name: Annotated[str,Field(min_length=3,max_length=50)]
    description: Optional[str] = None

class ScheduleResponse(BaseModel):
    id: int
    office: OfficeResponse
    date : date
    start_time: time
    end_time: time
    doctor: DoctorResponse
    is_available: bool

class ScheduleCreate(BaseModel):
    office_number:Annotated[str,Field(min_length=1,max_length=10)]
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
    office_id: int
    
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
    information: Optional[str] = None 
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
    medicament_id: int
    dosage: Optional[str] = None
    frequency: Optional[str] = None
    start_date: Optional[date] = Field(default_factory=lambda: date.today())
    end_date: Optional[date] = None
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


class PatientContraindicationsRequest(BaseModel):
    contradictions: List[str]

class PatientContraindicationDeleteRequest(BaseModel):
    contradiction: str


class CreateWithName(BaseModel):
    name: str

class PatientContr(BaseModel):
    patient_id: int
    contraindication_id: int

class PatientMedContr(BaseModel):
    patient_id: int
    contraindication_medicament_id: int

class MedicamentContr(BaseModel):
    medicament_id: int
    contraindication_id: int

class MedMedContr(BaseModel):
    first_medicament_id: int
    second_medicament_id: int


class MedicamentCreate(BaseModel):
    medicament_name: str
    med_contraindications_ids: List[int]
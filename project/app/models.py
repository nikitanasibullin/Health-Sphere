from database import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Date, Text, Time
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.sql.expression import text
from sqlalchemy import CheckConstraint


class Patient(Base):
    __tablename__= "patient"
    
    id=Column(Integer,primary_key=True,nullable=False)
    first_name=Column(String,nullable=False)
    last_name=Column(String,nullable=False)
    patronymic=Column(String,nullable=False)
    gender = Column(String,nullable=False)
    passport_number = Column(String,nullable=False, unique=True)
    insurance_number = Column(String,nullable=False, unique=True)
    phone_number = Column(String,nullable=False, unique=True)
    birth_date = Column(Date,nullable=False)

    email = Column(String,nullable=False, unique=True)
    password=Column(String,nullable=False)

    created_at = Column(TIMESTAMP(timezone=True),nullable=False,server_default = text('now()'))

    appointments = relationship("Appointment", back_populates="patient")
    medicaments = relationship("PatientMedicament", back_populates="patient", cascade="all, delete-orphan")
    contradictions = relationship("PatientContradiction", back_populates="patient", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint(
            "first_name ~ '^[A-Z][a-z]+$'",
            name='check_first_name_format'
        ),
        CheckConstraint(
            "last_name ~ '^[A-Z][a-z]+$'",
            name='check_last_name_format'
        ),
        CheckConstraint(
            "patronymic ~ '^[A-Z][a-z]+$'",
            name='check_patronymic_format'
        ),
        CheckConstraint(
            "phone_number ~ '^[0-9]+$'",
            name='check_phone_number_format'
        ),
        CheckConstraint(
            "email ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}$'",
            name='check_email_format'
        ),
        CheckConstraint(
            "gender IN ('female','male')",
            name='check_gender_format'
        )
    )


class Specialization(Base):
    __tablename__ = "specialization"
    
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False, unique=True)
    description = Column(Text)
    
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    
    # Define relationship back
    doctors = relationship("Doctor", back_populates="specialization")


class Doctor(Base):
    __tablename__= "doctor"
    
    id=Column(Integer,primary_key=True,nullable=False)
    first_name=Column(String,nullable=False)
    last_name=Column(String,nullable=False)
    patronymic=Column(String,nullable=False)
    phone_number = Column(String,nullable=False, unique=True)

    email = Column(String,nullable=False, unique=True)
    password=Column(String,nullable=False)
    specialization_id = Column(Integer, ForeignKey('specialization.id'), nullable=False)

    specialization = relationship("Specialization", back_populates="doctors")
    schedules = relationship("Schedule", back_populates="doctor")

    __table_args__ = (
        CheckConstraint(
            "first_name ~ '^[A-Z][a-z]+$'",
            name='check_first_name_format'
        ),
        CheckConstraint(
            "last_name ~ '^[A-Z][a-z]+$'",
            name='check_last_name_format'
        ),
        CheckConstraint(
            "patronymic ~ '^[A-Z][a-z]+$'",
            name='check_patronymic_format'
        ),
        CheckConstraint(
            "phone_number ~ '^[0-9]+$'",
            name='check_phone_number_format'
        ),
        CheckConstraint(
            "email ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}$'",
            name='check_email_format'
        )
    )

    created_at = Column(TIMESTAMP(timezone=True),nullable=False,server_default = text('now()'))




class Schedule(Base):
    __tablename__ = "schedule"
    
    id = Column(Integer, primary_key=True)
    doctor_id = Column(Integer, ForeignKey('doctor.id'), nullable=False)
    office_number = Column(String(10))
    date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    is_available = Column(Boolean, nullable=False, default=True)
    
    doctor = relationship("Doctor", back_populates="schedules")
    
    __table_args__ = (
        CheckConstraint("end_time > start_time", name='check_valid_time_range'),
        CheckConstraint("date >= CURRENT_DATE", name='check_future_date'),
    )

    appointment = relationship("Appointment", back_populates="schedule")

class Appointment(Base):
    __tablename__ = "appointment"
    
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey('patient.id'), nullable=False)
    schedule_id = Column(Integer, ForeignKey('schedule.id'), nullable=False)
    status = Column(String(50), nullable=False, default='scheduled')
    information = Column(Text)
    
    patient = relationship("Patient", back_populates="appointments")
    schedule = relationship("Schedule", back_populates="appointment")
    
    __table_args__ = (
        CheckConstraint(
            "status IN ('scheduled', 'completed', 'cancelled', 'no-show')", 
            name='check_valid_status'
        ),
    )


class Contradiction(Base):
    __tablename__ = "contradiction"
    
    medicament_name = Column(String(50), primary_key=True, nullable=False)
    contradiction = Column(String(50), primary_key=True, nullable=False)

    
class PatientMedicament(Base):
    __tablename__ = "patient_medicament"
    
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey('patient.id', ondelete='CASCADE'), nullable=False)
    medicament_name = Column(String(100), nullable=False)
    dosage = Column(String(50))
    frequency = Column(String(50))
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)
    prescribed_by = Column(String(100))  # кто назначил
    notes = Column(Text)
    
    patient = relationship("Patient", back_populates="medicaments")
    
    __table_args__ = (
        CheckConstraint("char_length(medicament_name) BETWEEN 1 AND 100", name='check_medicament_name_length'),
        CheckConstraint("end_date IS NULL OR end_date >= start_date", name='check_valid_dates'),
    )

class PatientContradiction(Base):
    __tablename__ = "patient_contradiction"
    
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey('patient.id', ondelete='CASCADE'), nullable=False)
    contradiction = Column(String(100), nullable=False)
    
    patient = relationship("Patient", back_populates="contradictions")
    
    __table_args__ = (
        CheckConstraint("char_length(contradiction) BETWEEN 1 AND 100", name='check_contradiction_name_length'),
    )
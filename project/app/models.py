from database import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Date, Text, Time
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.sql.expression import text
from sqlalchemy import CheckConstraint
import exceptions

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    user_type = Column(String, nullable=False)  # 'patient' или 'doctor'

    created_at = Column(TIMESTAMP(timezone=True),nullable=False,server_default = text('now()'))

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

    appointments = relationship("Appointment", back_populates="patient",
        cascade="all, delete-orphan")
    medicaments = relationship("PatientMedicament",back_populates="patient", cascade="all, delete-orphan")
    medicament_contraindications = relationship(
        "PatientMedicamentContraindication", 
        cascade="all, delete-orphan"
    )
    
    other_contraindications = relationship(
        "PatientOtherContraindication", 
        cascade="all, delete-orphan"
    )

    user_id = Column(Integer, ForeignKey('users.id'), unique=True, nullable=True)

    __table_args__ = (
        CheckConstraint(
            "first_name ~ '^[A-Z][a-z]*$'",
            name='check_first_name_format'
        ),
        CheckConstraint(
            "last_name ~ '^[A-Z][a-z]*$'",
            name='check_last_name_format'
        ),
        CheckConstraint(
            "patronymic ~ '^[A-Z][a-z]*$'",
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
    schedules = relationship("Schedule", back_populates="doctor",
        cascade="all, delete-orphan")

    user_id = Column(Integer, ForeignKey('users.id'), unique=True, nullable=True)

    __table_args__ = (
        CheckConstraint(
            "first_name ~ '^[A-Z][a-z]*$'",
            name='check_first_name_format'
        ),
        CheckConstraint(
            "last_name ~ '^[A-Z][a-z]*$'",
            name='check_last_name_format'
        ),
        CheckConstraint(
            "patronymic ~ '^[A-Z][a-z]*$'",
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
    office_id = Column(Integer, ForeignKey('office.id'), nullable=False) 
    date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    is_available = Column(Boolean, nullable=False, default=True)
    
    doctor = relationship("Doctor", back_populates="schedules")
    office = relationship("Office")
    
    created_at = Column(TIMESTAMP(timezone=True),nullable=False,server_default = text('now()'))

    __table_args__ = (
        CheckConstraint("end_time > start_time", name='check_valid_time_range'),
        CheckConstraint("date >= CURRENT_DATE", name='check_future_date'),
    )

    appointments = relationship("Appointment", back_populates="schedule",
        cascade="all, delete-orphan")

class Appointment(Base):
    __tablename__ = "appointment"
    
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey('patient.id'), nullable=False)
    schedule_id = Column(Integer, ForeignKey('schedule.id'), nullable=False)
    status = Column(String(50), nullable=False, default='scheduled')
    information = Column(Text)
    
    patient = relationship("Patient", back_populates="appointments")
    schedule = relationship("Schedule", back_populates="appointments")

    created_at = Column(TIMESTAMP(timezone=True),nullable=False,server_default = text('now()'))
    
    __table_args__ = (
        CheckConstraint(
            "status IN ('scheduled', 'completed', 'cancelled', 'no-show')", 
            name='check_valid_status'
        ),
    )


    
class PatientMedicament(Base):
    __tablename__ = "patient_medicament"
    
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey('patient.id', ondelete='CASCADE'), nullable=False)
    medicament_id = Column(Integer, ForeignKey('medicament.id'), nullable=False)
    dosage = Column(String(50))
    frequency = Column(String(50))
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)
    doctor_by_id = Column(Integer, ForeignKey('doctor.id'))
    appointment_id = Column(Integer, ForeignKey('appointment.id'))
    notes = Column(Text)
    
    patient = relationship("Patient", back_populates="medicaments")
    medicament = relationship("Medicament")
    doctor = relationship("Doctor", foreign_keys=[doctor_by_id])
    appointment = relationship("Appointment")

    created_at = Column(TIMESTAMP(timezone=True),nullable=False,server_default = text('now()'))
    
    __table_args__ = (
        CheckConstraint("end_date IS NULL OR end_date >= start_date", name='check_valid_dates'),
    )


class Office(Base):
    __tablename__ = "office"
    
    id = Column(Integer, primary_key=True)
    number = Column(String(15),nullable=False,unique=True)

    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

class Medicament(Base):
    __tablename__ = "medicament"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(30),nullable=False,unique=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))


class OtherContraindication(Base):
    __tablename__ = "other_contraindication"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)
    
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))


class MedicationContraindicationOther(Base):
    __tablename__ = "medication_contraindication_other"
    
    medicament_id = Column(Integer, ForeignKey('medicament.id'), primary_key=True)
    contraindication_id = Column(Integer, ForeignKey('other_contraindication.id'), primary_key=True)

    medicament = relationship("Medicament")
    contraindication = relationship("OtherContraindication")
    
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

class MedicamentMedicamentContraindication(Base):
    __tablename__ = "medicament_medicament_contraindication"
    
    medication_first_id = Column(Integer, ForeignKey('medicament.id'), primary_key=True)
    medication_second_id = Column(Integer, ForeignKey('medicament.id'), primary_key=True)

    first_medicament = relationship("Medicament", foreign_keys=[medication_first_id])
    second_medicament = relationship("Medicament", foreign_keys=[medication_second_id])


    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    
    __table_args__ = (
        CheckConstraint("medication_first_id < medication_second_id", name='check_different_medicaments'),
    )



class PatientMedicamentContraindication(Base):
    __tablename__ = "patient_medicament_contraindication"
    
    patient_id = Column(Integer, ForeignKey('patient.id'), primary_key=True)
    medicament_id = Column(Integer, ForeignKey('medicament.id'), primary_key=True)
    medicament = relationship("Medicament")

    
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))


class PatientOtherContraindication(Base):
    __tablename__ = "patient_other_contradictions"
    
    patient_id = Column(Integer, ForeignKey('patient.id'), primary_key=True)
    contraindication_id = Column(Integer, ForeignKey('other_contraindication.id'), primary_key=True)
    contraindication = relationship("OtherContraindication")
    
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
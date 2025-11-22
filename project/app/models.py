from database import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Date
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

    __table_args__ = (
        CheckConstraint(
            "first_name ~ '^[A-Z][a-z]+$'",
            name='check_first_name_format'
        ),
        CheckConstraint(
            "last_name ~ '^[a-z][a-z]+$'",
            name='check_last_name_format'
        ),
        CheckConstraint(
            "patronymic ~ '^[a-z][a-z]+$'",
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
        ),
    )
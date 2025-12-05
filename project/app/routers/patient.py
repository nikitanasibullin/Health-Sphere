import models,schemas
from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from database import get_db
from typing import Optional,List
from sqlalchemy import func
from datetime import date
router = APIRouter(
    prefix = "/patient",
    tags=['patient']
)

@router.post("/registration", response_model=dict)
def create_patient(
    patient: schemas.PatientCreate,
    db: Session = Depends(get_db)
):

    try:
        # Просто создаем объект доктора
        db_patient = models.Patient(**patient.model_dump())
        
        # Добавляем в базу
        db.add(db_patient)
        db.commit()
        
        return {
            "status": "success",
            "patient_id": db_patient.id,
            "message": f"Пациент {patient.first_name} создан"
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Ошибка: {str(e)}"
        )
    

@router.get("/doctors",response_model=List[schemas.DoctorResponse])
def get_doctors(db: Session = Depends(get_db)):
    doctors= db.query(models.Doctor).all()
    return doctors

@router.get("/schedule/{doctor_id}",response_model=List[schemas.ScheduleResponse])
def get_doctors_schedule(doctor_id: int, db: Session = Depends(get_db)):
    doctor = db.query(models.Doctor).filter(models.Doctor.id == doctor_id).first()
    
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Врач с ID {doctor_id} не найден"
        )
    
    # Создаем базовый запрос с использованием relationship
    query = db.query(models.Schedule)\
        .filter(models.Schedule.doctor_id == doctor_id)
    
    # Сортируем результаты
    schedules = query.order_by(
        models.Schedule.date.asc(),
        models.Schedule.start_time.asc()
    ).all()
    
    return schedules

@router.post("/appointments/{patient_id}/{schedule_id}", response_model=schemas.AppointmentResponseToPatient)
def create_appointment(
    patient_id: int,  # ID пациента можно получать из токена
    schedule_id: int,
    db: Session = Depends(get_db)
):
    """
    Создание записи на прием к врачу.
    """
    try:
        #Проверяем существование пациента
        patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пациент не найден"
            )
        
        schedule = db.query(models.Schedule)\
            .filter(models.Schedule.id == schedule_id)\
            .first()
        
        if not schedule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Расписание не найдено"
            )
        
        if not schedule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Расписание не найдено"
            )
        
        #Проверяем доступность расписания
        if not schedule.is_available:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Данное время уже занято"
            )
        
        #роверяем, что дата не в прошлом
        if schedule.date < date.today():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Нельзя записаться на прошедшую дату"
            )
        
        #Проверяем, нет ли уже записи у пациента на это время
        existing_appointment = db.query(models.Appointment)\
            .filter(
                models.Appointment.patient_id == patient_id,
                models.Appointment.schedule_id ==schedule_id
            )\
            .first()
        
        if existing_appointment:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="У вас уже есть запись на это время"
            )
        
        # 7. Создаем запись на прием
        db_appointment = models.Appointment(
            patient_id=patient_id,
            schedule_id=schedule_id,
            status='scheduled'
        )
        
        db.add(db_appointment)
        
        # 8. Обновляем расписание - помечаем как занятое
        schedule.is_available = False
        
        db.commit()
       
        return db_appointment
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при создании записи: {str(e)}"
        )

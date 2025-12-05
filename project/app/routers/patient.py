import models,schemas
from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from database import get_db
from typing import Optional,List
from sqlalchemy import func

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

import models,schemas
from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from database import get_db
from typing import Optional,List
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

router = APIRouter(
    prefix = "/admin",
    tags=['admin']
)

@router.post("/specializations", 
             response_model=schemas.SpecializationCreate,
             status_code=status.HTTP_201_CREATED,
             summary="Создать новую специализацию")
def create_specialization(
    specialization: schemas.SpecializationCreate,
    db: Session = Depends(get_db)
):

    try:
        # Проверяем, существует ли уже такая специализация
        existing = db.query(models.Specialization)\
            .filter(models.Specialization.name.ilike(specialization.name))\
            .first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Специализация с таким названием уже существует"
            )
        
        # Создаем новую специализацию
        db_specialization = models.Specialization(
            name=specialization.name,
            description=specialization.description
        )
        
        db.add(db_specialization)
        db.commit()
        
        return db_specialization
        
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ошибка при создании специализации"
        )

@router.get("/specializations",
            response_model=List[schemas.SpecializationResponse],
            summary="Получить все специализации")
def get_all_specializations(db: Session = Depends(get_db)):
    """Получить список всех медицинских специализаций."""
    specializations = next(db.query(models.Specialization).first())
    return specializations


@router.post("/doctors", response_model=dict)
def create_doctor_simple(
    doctor: schemas.DoctorCreate,
    db: Session = Depends(get_db)
):

    try:
        # Просто создаем объект доктора
        db_doctor = models.Doctor(**doctor.model_dump())
        
        # Добавляем в базу
        db.add(db_doctor)
        db.commit()
        
        return {
            "status": "success",
            "doctor_id": db_doctor.id,
            "message": f"Доктор {doctor.first_name} создан"
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Ошибка: {str(e)}"
        )
    
    
def delete_doctor(
    doctor_id: int,
    db: Session = Depends(get_db)
):
    doctor = db.query(models.Doctor)\
        .filter(models.Doctor.id == doctor_id)\
        .first()
    
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Врач с ID {doctor_id} не найден"
        )
    
    try:
        # appointments = db.query(models.Appointment)\
        #     .filter(models.Appointment.doctor_id == doctor_id)\
        #     .count()
        # 
        # if appointments > 0:
        #     raise HTTPException(
        #         status_code=status.HTTP_400_BAD_REQUEST,
        #         detail="Нельзя удалить врача, у которого есть записи на прием"
        #     )
        
        db.delete(doctor)
        db.commit()
        
        return Response(status_code=status.HTTP_204_NO_CONTENT)
        
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Нельзя удалить врача: {str(e)}"
        )

@router.get("/doctors/search/{search_term}",
            response_model=List[schemas.DoctorResponse],
            summary="Поиск врачей")
def search_doctors(
    search_term: str,
    db: Session = Depends(get_db)
):
    doctors = db.query(models.Doctor)\
        .filter(
            (models.Doctor.first_name.ilike(f"%{search_term}%")) |
            (models.Doctor.last_name.ilike(f"%{search_term}%")) |
            (models.Doctor.middle_name.ilike(f"%{search_term}%")) |
            (models.Doctor.specialization.has(
                models.Specialization.name.ilike(f"%{search_term}%")
            ))
        )\
        .all()
    
    return doctors
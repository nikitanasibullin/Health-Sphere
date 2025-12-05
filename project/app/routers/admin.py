import models,schemas
from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from database import get_db
from typing import Optional,List
from sqlalchemy import func, and_
from sqlalchemy.exc import IntegrityError
from datetime import timedelta

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


@router.get("/patients",
            response_model=List[schemas.PatientResponse],
            summary="Получить всех пациентов ")
def get_all_specializations(db: Session = Depends(get_db)):
    """Получить список всех медицинских специализаций."""
    specializations = db.query(models.Patient).all()
    return specializations


@router.get("/specializations",
            response_model=List[schemas.SpecializationResponse],
            summary="Получить все специализации")
def get_all_specializations(db: Session = Depends(get_db)):
    """Получить список всех медицинских специализаций."""
    specializations = db.query(models.Specialization).all()
    return specializations


@router.post("/doctors", response_model=dict)
def create_doctor(
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
    
@router.post("/schedule", response_model=dict)
def create_schedule(
    schedule: schemas.ScheduleCreate,
    db: Session = Depends(get_db)
):

    try:
        # Просто создаем объект доктора
        db_schedule = models.Schedule(**schedule.model_dump())
        
        # Добавляем в базу
        db.add(db_schedule)
        db.commit()
        
        return {
            "status": "success",
            "doctor_id": db_schedule.id,
            "message": f"Расписание создано"
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=f"Ошибка: {str(e)}"
        )
    
@router.post("/schedule/batch", 
            response_model=dict,
            summary="Создать слоты равной длины")
def create_schedule_batch(
    schedule: schemas.ScheduleBatchCreate,
    db: Session = Depends(get_db)
):
    """
    Делит интервал на N равных слотов без перерывов.
    
    Пример:
    {
        "doctor_id": 1,
        "date": "2024-01-20",
        "start_time": "09:00:00",
        "end_time": "13:00:00",
        "slots_count": 4
    }
    Создаст 4 слота по 1 часу: 9-10, 10-11, 11-12, 12-13
    """
    try:
        # Проверяем врача
        doctor = db.query(models.Doctor)\
            .filter(models.Doctor.id == schedule.doctor_id)\
            .first()
        
        if not doctor:
            raise HTTPException(404, f"Врач с ID {schedule.doctor_id} не найден")
        
        # Проверяем время
        if schedule.end_time <= schedule.start_time:
            raise HTTPException(400, "Конечное время должно быть больше начального")
        
        if schedule.slots_count <= 0:
            raise HTTPException(400, "Количество слотов должно быть больше 0")
        
        # Преобразуем время в секунды для расчетов
        start_seconds = schedule.start_time.hour * 3600 + schedule.start_time.minute * 60
        end_seconds = schedule.end_time.hour * 3600 + schedule.end_time.minute * 60
        
        # Общая длительность в секундах
        total_duration = end_seconds - start_seconds
        
        # Длительность одного слота в секундах
        slot_duration = total_duration // schedule.slots_count
        
        if slot_duration <= 0:
            raise HTTPException(400, "Слишком много слотов для такого интервала")
        
        # Переводим секунды обратно в часы и минуты
        slot_hours = slot_duration // 3600
        slot_minutes = (slot_duration % 3600) // 60
        
        created_slots = []
        
        # Создаем слоты
        current_seconds = start_seconds
        
        for i in range(schedule.slots_count):
            # Вычисляем начало и конец слота
            slot_start_seconds = current_seconds
            slot_end_seconds = slot_start_seconds + slot_duration
            
            # Конвертируем секунды в time
            from datetime import time as dt_time
            
            start_hour = slot_start_seconds // 3600
            start_minute = (slot_start_seconds % 3600) // 60
            
            end_hour = slot_end_seconds // 3600
            end_minute = (slot_end_seconds % 3600) // 60
            
            slot_start_time = dt_time(start_hour, start_minute)
            slot_end_time = dt_time(end_hour, end_minute)
            
            # Проверяем пересечения
            existing_slot = db.query(models.Schedule)\
                .filter(
                    models.Schedule.doctor_id == schedule.doctor_id,
                    models.Schedule.date == schedule.date,
                    models.Schedule.start_time < slot_end_time,
                    models.Schedule.end_time > slot_start_time
                )\
                .first()
            
            if existing_slot:
                raise HTTPException(
                    400,
                    f"Слот {i+1} пересекается с существующим: "
                    f"{existing_slot.start_time} - {existing_slot.end_time}"
                )
            
            # Создаем слот
            db_slot = models.Schedule(
                doctor_id=schedule.doctor_id,
                office_number=schedule.office_number,
                date=schedule.date,
                start_time=slot_start_time,
                end_time=slot_end_time,
                is_available=True
            )
            
            db.add(db_slot)
            created_slots.append({
                'slot': i + 1,
                'start': slot_start_time.isoformat()[:5],  # HH:MM
                'end': slot_end_time.isoformat()[:5]
            })
            
            # Переходим к следующему слоту
            current_seconds = slot_end_seconds
        
        db.commit()
        
        return {
            "status": "success",
            "doctor_id": schedule.doctor_id,
            "date": schedule.date.isoformat(),
            "total_slots": len(created_slots),
            "slot_duration_minutes": slot_duration // 60,
            "slots": created_slots,
            "message": f"Создано {len(created_slots)} слотов по {slot_duration//60} минут"
        }
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(500, f"Ошибка: {str(e)}")
    
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
import models,schemas, oauth2, utils
from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from database import get_db
from typing import Optional,List
from sqlalchemy import func, and_
from sqlalchemy.exc import IntegrityError
from datetime import timedelta
import exceptions

router = APIRouter(
    prefix = "/api/admin",
    tags=['admin']
)

@router.post("/specializations", 
             response_model=schemas.SpecializationCreate,
             status_code=status.HTTP_201_CREATED)
@exceptions.handle_exceptions(custom_message="Не удалось создать специализацию")
def create_specialization(
    specialization: schemas.SpecializationCreate,
    current_admin = Depends(oauth2.get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Создать специализацию.
    """

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
        name=specialization.name.capitalize(),
        description=specialization.description
    )
    
    db.add(db_specialization)
    db.commit()
    
    return db_specialization

@router.get("/patients",
            response_model=List[schemas.PatientResponse])
@exceptions.handle_exceptions(custom_message="Не удалось получить список всех пациентов")
def get_all_specializations(db: Session = Depends(get_db),current_admin = Depends(oauth2.get_current_admin)):
    """
    Получение списка всех пациентов.
    """
    specializations = db.query(models.Patient).all()
    return specializations

@router.get("/appointments",
            response_model=List[schemas.AppointmentResponse])
@exceptions.handle_exceptions(custom_message="Не удалось получить список всех записей")
def get_all_specializations(db: Session = Depends(get_db),current_admin = Depends(oauth2.get_current_admin)):
    """
    Получение всех записей к врачам
    """
    appointments = db.query(models.Appointment).all()
    return appointments


@router.get("/specializations",
            response_model=List[schemas.SpecializationResponse])
@exceptions.handle_exceptions(custom_message="Не удалось получить все специализации")
def get_all_specializations(db: Session = Depends(get_db),current_admin = Depends(oauth2.get_current_admin)):
    """Получить список всех медицинских специализаций."""
    specializations = db.query(models.Specialization).all()
    return specializations


@router.post("/doctor", response_model=schemas.Token)
@exceptions.handle_exceptions(custom_message="Не удалось создать врача")
def register_doctor(
    doctor_data: schemas.DoctorCreate,
    current_admin = Depends(oauth2.get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Регистрация врача с созданием пользователя и профиля врача
    """
    # Проверяем, существует ли пользователь с таким email
    existing_user = db.query(models.User).filter(
        models.User.email == doctor_data.email
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже существует"
        )
    
    # Проверяем уникальность данных врача
    existing_doctor = db.query(models.Doctor).filter(
        (models.Doctor.email == doctor_data.email) |
        (models.Doctor.phone_number == doctor_data.phone_number)
    ).first()
    
    if existing_doctor:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Врач с такими данными уже существует"
        )
    
    # Хешируем пароль
    hashed_password = utils.hash(doctor_data.password)

    first_name_normalized = (
        doctor_data.first_name.capitalize() 
        if doctor_data.first_name 
        else None
    )
    
    last_name_normalized = (
        doctor_data.last_name.capitalize() 
        if doctor_data.last_name 
        else None
    )
    
    patronymic_normalized = (
        doctor_data.patronymic.capitalize() 
        if doctor_data.patronymic 
        else None
    )
    
    # 1. СОЗДАЕМ ПОЛЬЗОВАТЕЛЯ
    db_user = models.User(
        email=doctor_data.email,
        password=hashed_password,
        user_type='doctor',
    )
    
    db.add(db_user)
    db.flush()
    
    # 2. СОЗДАЕМ ПРОФИЛЬ ВРАЧА
    db_doctor = models.Doctor(
        first_name=first_name_normalized,
        last_name=last_name_normalized,
        patronymic=patronymic_normalized,
        phone_number=doctor_data.phone_number,
        email=doctor_data.email,
        password=hashed_password,  # для совместимости
        specialization_id=doctor_data.specialization_id,
        user_id=db_user.id  # связь с users
    )
    
    db.add(db_doctor)
    db.flush()
    db_user.user_type_id = db_doctor.id
    
    db.commit()
    
    # Создаем токен
    access_token = oauth2.create_access_token(
        data={
            "user_id": db_user.id,
            "user_type": 'doctor'
        }
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_type": "doctor"
    }

    
@router.post("/schedule", response_model=dict)
@exceptions.handle_exceptions(custom_message="Не удалось создать расписание")
def create_schedule(
    schedule: schemas.ScheduleCreate,
    db: Session = Depends(get_db),
    current_admin = Depends(oauth2.get_current_admin)
):
    """
    Создание одного расписания
    """
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
        

    
@router.post("/schedule/batch", 
            response_model=dict)
@exceptions.handle_exceptions(custom_message="Не удалось создать расписание")
def create_schedule_batch(
    schedule: schemas.ScheduleBatchCreate,
    current_admin = Depends(oauth2.get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Делит интервал на N равных слотов без перерывов и создаёт расписания.
    Создаст 4 слота по 1 часу: 9-10, 10-11, 11-12, 12-13
    """

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



@router.delete("/doctor/{doctor_id}", 
               status_code=status.HTTP_204_NO_CONTENT)
@exceptions.handle_exceptions(custom_message="Не удалось удалить доктора")
def delete_doctor(
    doctor_id: int,
    current_admin = Depends(oauth2.get_current_admin),
    db: Session = Depends(get_db)
    
):
    """
    Удаление врача
    """
    # Находим врача и пользователя
    doctor = db.query(models.Doctor)\
        .filter(models.Doctor.id == doctor_id)\
        .first()
    
    if not doctor:
        raise HTTPException(404, f"Врач с ID {doctor_id} не найден")
    
    user_id = doctor.user_id
    
    # 1. ОБНУЛЯЕМ user_id у врача
    doctor.user_id = None
    db.add(doctor)
    db.flush()
    
    # 2. Удаляем расписания и записи
    schedules = db.query(models.Schedule)\
        .filter(models.Schedule.doctor_id == doctor_id)\
        .all()
    
    for schedule in schedules:
        db.query(models.Appointment)\
            .filter(models.Appointment.schedule_id == schedule.id)\
            .delete(synchronize_session=False)
    
    db.query(models.Schedule)\
        .filter(models.Schedule.doctor_id == doctor_id)\
        .delete(synchronize_session=False)
    
    # 3. Удаляем врача
    db.delete(doctor)
    
    # 4. КОММИТ первой транзакции
    db.commit()
    
    try:
        db.query(models.User)\
            .filter(models.User.id == user_id)\
            .delete(synchronize_session=False)
        db.commit()
    finally:
        db.close()

    return Response(status_code=204)



@router.delete("/patient/{patient_id}", 
               status_code=status.HTTP_204_NO_CONTENT)
@exceptions.handle_exceptions(custom_message="Не удалось удалить пациента")
def delete_patient(
    patient_id: int,
    current_admin = Depends(oauth2.get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Удаление пациента
    """
    # Находим врача и пользователя
    patient = db.query(models.Patient)\
        .filter(models.Patient.id == patient_id)\
        .first()
    
    if not patient:
        raise HTTPException(404, f"Пациент с ID {patient_id} не найден")
    
    user_id = patient.user_id
    
    # 1. ОБНУЛЯЕМ user_id у врача
    patient.user_id = None
    db.add(patient)
    db.flush()
    
    
    
    db.query(models.Appointment)\
        .filter(models.Appointment.patient_id == patient_id)\
        .delete(synchronize_session=False)
    
    # 3. Удаляем врача
    db.delete(patient)
    
    # 4. КОММИТ первой транзакции
    db.commit()
    
    try:
        db.query(models.User)\
            .filter(models.User.id == user_id)\
            .delete(synchronize_session=False)
        db.commit()
    finally:
        db.close()

    return Response(status_code=204)


@router.delete("/schedule/{schedule_id}", 
               status_code=status.HTTP_204_NO_CONTENT)
@exceptions.handle_exceptions(custom_message="Не удалось удалить расписание")
def delete_schedule(
    schedule_id: int,
    current_admin = Depends(oauth2.get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Удаление расписания по ID с каскадным удалением связанных приемов
    """
    # Находим расписание
    schedule = db.query(models.Schedule)\
        .filter(models.Schedule.id == schedule_id)\
        .first()
    
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Расписание с ID {schedule_id} не найдено"
        )
    
    #удаляем все связанные приемы
    deleted_appointments_count = db.query(models.Appointment)\
        .filter(models.Appointment.schedule_id == schedule_id)\
        .delete(synchronize_session=False)
    
    # Удаляем само расписание
    db.delete(schedule)
    db.commit()
    

    
    return Response(status_code=204)


@router.delete("/appointments/{appointment_id}", 
               status_code=status.HTTP_204_NO_CONTENT)
@exceptions.handle_exceptions(custom_message="Не удалось удалить запись на прием")
def delete_appointment(
    appointment_id: int,
    current_admin = Depends(oauth2.get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Удаление записи на прием по ID
    """
    # Находим запись на прием
    appointment = db.query(models.Appointment)\
        .filter(models.Appointment.id == appointment_id)\
        .first()
    
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Запись на прием с ID {appointment_id} не найдена"
        )
    
        # Освобождаем слот в расписании
    schedule = db.query(models.Schedule)\
        .filter(models.Schedule.id == appointment.schedule_id)\
        .first()
    # Удаляем запись
    db.delete(appointment)
    db.commit()
    
    
    if schedule:
        schedule.is_available = True
        db.add(schedule)
        db.commit()
    
    
    return Response(status_code=204)




@router.get("/doctors/search/{search_term}",
            response_model=List[schemas.DoctorResponse])
@exceptions.handle_exceptions(custom_message="Не удалось получить список докторов")
def search_doctors(
    search_term: str,
    db: Session = Depends(get_db),
    current_admin = Depends(oauth2.get_current_admin)
):
    """
    Поиск доктора по фамилии\имени\отчеству\специализации
    """
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


@router.get("/doctors",
            response_model=List[schemas.DoctorResponse])
@exceptions.handle_exceptions(custom_message="Не удалось получить список докторов")
def search_doctors(
    db: Session = Depends(get_db),
    current_admin = Depends(oauth2.get_current_admin)
):
    """
    Поиск доктора по фамилии\имени\отчеству\специализации
    """
    doctors = db.query(models.Doctor).all()
    
    return doctors



@router.get("/doctors",response_model=List[schemas.DoctorResponseAdmin])
@exceptions.handle_exceptions(custom_message="Не удалось получить список докторов")
def get_doctors(db: Session = Depends(get_db),current_admin = Depends(oauth2.get_current_admin)):
    """
    Получение списка всех докторов
    """
    doctors= db.query(models.Doctor).all()
    return doctors


@router.get("/schedule/{doctor_id}",response_model=List[schemas.ScheduleResponse])
@exceptions.handle_exceptions(custom_message="Не удалось получить расписание доктора")
def get_doctors_schedule(doctor_id: int,current_admin = Depends(oauth2.get_current_admin), 
                         db: Session = Depends(get_db)):
    """
    Получение расписания определенного врача
    """
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

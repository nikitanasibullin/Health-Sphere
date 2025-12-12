import models,schemas, utils, oauth2
from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from database import get_db
from typing import Optional,List
from sqlalchemy import func
from datetime import date
from datetime import datetime
router = APIRouter(
    prefix = "/patient",
    tags=['patient']
)

# auth.py
@router.post("/register", response_model=schemas.Token)
def register_patient(
    patient_data: schemas.PatientCreate,
    db: Session = Depends(get_db)
):
    """
    Регистрация пациента с созданием пользователя и профиля
    """
    # Проверяем, существует ли пользователь с таким email
    existing_user = db.query(models.User).filter(
        models.User.email == patient_data.email
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже существует"
        )
    
    # Проверяем уникальность данных пациента
    existing_patient = db.query(models.Patient).filter(
        (models.Patient.email == patient_data.email) |
        (models.Patient.phone_number == patient_data.phone_number) |
        (models.Patient.passport_number == patient_data.passport_number) |
        (models.Patient.insurance_number == patient_data.insurance_number)
    ).first()
    
    if existing_patient:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пациент с такими данными уже существует"
        )
    
    first_name_normalized = (
        patient_data.first_name.capitalize() 
        if patient_data.first_name 
        else None
    )
    
    last_name_normalized = (
        patient_data.last_name.capitalize() 
        if patient_data.last_name 
        else None
    )
    
    patronymic_normalized = (
        patient_data.patronymic.capitalize() 
        if patient_data.patronymic 
        else None
    )

    # Хешируем пароль
    hashed_password = utils.hash(patient_data.password)
    
    # 1. СОЗДАЕМ ПОЛЬЗОВАТЕЛЯ в таблице users
    db_user = models.User(
        email=patient_data.email,
        password=hashed_password,
        user_type='patient',
    )
    
    db.add(db_user)
    db.flush()  # Получаем ID пользователя (user.id)
    
    # 2. СОЗДАЕМ ПРОФИЛЬ ПАЦИЕНТА
    db_patient = models.Patient(
        first_name=first_name_normalized,
        last_name=last_name_normalized,
        patronymic=patronymic_normalized,
        gender=patient_data.gender,
        passport_number=patient_data.passport_number,
        insurance_number=patient_data.insurance_number,
        birth_date=patient_data.birth_date,
        phone_number=patient_data.phone_number,
        email=patient_data.email,
        password=hashed_password,  # Дублируем для совместимости со старым кодом
        user_id=db_user.id  # ВАЖНО: связь с таблицей users
    )
    
    db.add(db_patient)
    db.flush()  # Получаем ID пациента (patient.id)
    
    # 3. ОБНОВЛЯЕМ ПОЛЬЗОВАТЕЛЯ ссылкой на профиль
    db_user.user_type_id = db_patient.id
    
    db.commit()
    
    # Создаем токен для автоматического входа
    access_token = oauth2.create_access_token(
        data={
            "user_id": db_user.id,
            "user_type": 'patient'
        }
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_type": "patient"
    }
    

@router.get("/doctors",response_model=List[schemas.DoctorResponse])
def get_doctors(db: Session = Depends(get_db),current_patient: models.Patient = Depends(oauth2.get_current_patient)):
    doctors= db.query(models.Doctor).all()
    return doctors

@router.get("/schedule/{doctor_id}",response_model=List[schemas.ScheduleResponse])
def get_doctors_schedule(doctor_id: int,current_patient: models.Patient = Depends(oauth2.get_current_patient), db: Session = Depends(get_db)):
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


@router.get("/appointments", response_model=List[schemas.AppointmentResponseToPatient])
def get_my_appointments(
    current_patient: models.Patient = Depends(oauth2.get_current_patient),
    db: Session = Depends(get_db)
):
    """
    Получение всех записей на прием текущего пациента
    """
    try:
        appointments = db.query(models.Appointment)\
            .filter(models.Appointment.patient_id == current_patient.id,models.Appointment.status=="scheduled")\
            .order_by(models.Appointment.id.desc())\
            .all()
        
        return appointments
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении записей: {str(e)}"
        )


@router.get("/appointments", response_model=List[schemas.AppointmentResponseToPatient])
def get_my_appointments(
    current_patient: models.Patient = Depends(oauth2.get_current_patient),
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Получение всех записей на прием текущего пациента
    """
    try:
        appointments = db.query(models.Appointment)\
            .filter(
            models.Appointment.patient_id == current_patient.id
            )
        if status_filter:
            appointments = appointments.filter(models.Appointment.status == status_filter)
        appointments = appointments.order_by(models.Appointment.id.desc()).all()
        return appointments

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении записей: {str(e)}"
        )


@router.post("/appointments/{schedule_id}", response_model=schemas.AppointmentResponseToPatient)
def create_appointment(
    schedule_id: int,
    current_patient: models.Patient = Depends(oauth2.get_current_patient),  # Получаем пациента из токена
    db: Session = Depends(get_db)
):
    """
    Создание записи на прием к врачу.
    Пациент создает запись на себя автоматически.
    """
    try:
        # Получаем пациента из токена (уже проверено в get_current_patient)
        patient_id = current_patient.id
        
        # Проверяем существование расписания
        schedule = db.query(models.Schedule)\
            .filter(models.Schedule.id == schedule_id)\
            .first()
        
        if not schedule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Расписание не найдено"
            )
        
        # Проверяем доступность расписания
        if not schedule.is_available:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Данное время уже занято"
            )
        
        # Проверяем, что дата не в прошлом
        if schedule.date < date.today():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Нельзя записаться на прошедшую дату"
            )
        
        # Проверяем, нет ли уже записи у пациента на это время
        existing_appointment = db.query(models.Appointment)\
            .filter(
                models.Appointment.patient_id == patient_id,
                models.Appointment.schedule_id == schedule_id
            )\
            .first()
        
        if existing_appointment:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="У вас уже есть запись на это время"
            )
        
        # Создаем запись на прием
        db_appointment = models.Appointment(
            patient_id=patient_id,
            schedule_id=schedule_id,
            status='scheduled'
        )
        
        db.add(db_appointment)
        
        # Обновляем расписание - помечаем как занятое
        schedule.is_available = False
        
        db.commit()
        db.refresh(db_appointment)
        
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
    
@router.delete("/appointments/{appointment_id}")
def cancel_appointment(
    appointment_id: int,
    current_patient: models.Patient = Depends(oauth2.get_current_patient),
    db: Session = Depends(get_db)
):
    """
    Отмена записи на прием
    """
    try:
        # Находим запись
        appointment = db.query(models.Appointment)\
            .filter(
                models.Appointment.id == appointment_id,
                models.Appointment.patient_id == current_patient.id
            )\
            .first()
        
        if not appointment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Запись не найдена"
            )
        
        # Проверяем, можно ли отменить (не меньше чем за 24 часа до приема)
        schedule = db.query(models.Schedule)\
            .filter(models.Schedule.id == appointment.schedule_id)\
            .first()
        
        if schedule:
            appointment_datetime = datetime.combine(schedule.date, schedule.start_time)
            time_diff = appointment_datetime - datetime.now()
            
            if time_diff.total_seconds() < 24 * 60 * 60:  # меньше 24 часов
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Отменить запись можно не позднее чем за 24 часа до приема"
                )
            
            # Освобождаем расписание
            schedule.is_available = True
        
        # Обновляем статус записи
        appointment.status = 'cancelled'
        
        db.commit()
        
        return {
            "message": "Запись успешно отменена",
            "appointment_id": appointment_id
        }
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при отмене записи: {str(e)}"
        )
    

@router.get("/medication", response_model=dict)
def get_patient_medication_report(
    current_patient: models.Patient = Depends(oauth2.get_current_patient),
    db: Session = Depends(get_db)
):
    """
    Полный отчет о лекарствах и противопоказаниях пациента.
    Возвращает лекарства пациента + все противопоказания (прямые и из базы лекарств).
    """
    try:

        patient_id=current_patient.id
        # Проверяем существование пациента
        patient = db.query(models.Patient)\
            .filter(models.Patient.id == patient_id)\
            .first()
        
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Пациент с ID {patient_id} не найден"
            )
        
        # 1. Получаем все лекарства пациента
        patient_medicaments = db.query(models.PatientMedicament)\
            .filter(models.PatientMedicament.patient_id == patient_id)\
            .order_by(models.PatientMedicament.start_date.desc())\
            .all()
        
        # 2. Получаем прямые противопоказания пациента
        patient_contradictions = db.query(models.PatientContradiction)\
            .filter(models.PatientContradiction.patient_id == patient_id)\
            .all()
        
        # 3. Получаем названия лекарств пациента
        medicament_names = [pm.medicament_name for pm in patient_medicaments]
        
        # 4. Получаем противопоказания для лекарств пациента из общей базы
        medicament_contradictions = []
        if medicament_names:
            medicament_contradictions = db.query(models.Contradiction)\
                .filter(models.Contradiction.medicament_name.in_(medicament_names))\
                .all()
        
        # 5. Формируем отчет
        report = {
            "patient_info": {
                "id": patient.id,
                "full_name": f"{patient.last_name} {patient.first_name} {patient.patronymic}",
                "birth_date": patient.birth_date
            },
            "medicaments": [
                {
                    "id": pm.id,
                    "name": pm.medicament_name,
                    "dosage": pm.dosage,
                    "frequency": pm.frequency,
                    "start_date": pm.start_date,
                    "end_date": pm.end_date,
                    "prescribed_by": pm.prescribed_by,
                    "is_active": pm.end_date is None or pm.end_date >= date.today()
                }
                for pm in patient_medicaments
            ],
            "direct_contraindications": [
                {
                    "id": pc.id,
                    "contradiction": pc.contradiction
                }
                for pc in patient_contradictions
            ],
            "medicament_based_contraindications": [
                {
                    "medicament_name": mc.medicament_name,
                    "contradiction": mc.contradiction
                }
                for mc in medicament_contradictions
            ],
            "summary": {
                "total_medicaments": len(patient_medicaments),
                "active_medicaments": len([pm for pm in patient_medicaments 
                                         if pm.end_date is None or pm.end_date >= date.today()]),
                "total_direct_contraindications": len(patient_contradictions),
                "total_medicament_contraindications": len(medicament_contradictions)
            }
        }
        
        return report
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении отчета: {str(e)}"
        )
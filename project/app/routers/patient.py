import models,schemas, utils, oauth2
from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session,joinedload
from database import get_db
from typing import Optional,List
from sqlalchemy import func
from datetime import date
from datetime import datetime
import exceptions

router = APIRouter(
    prefix = "/api/patient",
    tags=['patient']
)

# auth.py
@router.post("/register", response_model=schemas.Token)
@exceptions.handle_exceptions(custom_message="Не удалось создать пациента")
def register_patient(
    patient_data: schemas.PatientCreate,
    db: Session = Depends(get_db)
):
    """
    Регистрация пациента с созданием пользователя и профиля пациента.
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
@exceptions.handle_exceptions(custom_message="Не удалось получить список докторов")
def get_doctors(db: Session = Depends(get_db),current_patient: models.Patient = Depends(oauth2.get_current_patient)):
    """
    Получение списка всех докторов
    """
    doctors= db.query(models.Doctor).all()
    return doctors

@router.get("/schedule/{doctor_id}",response_model=List[schemas.ScheduleResponse])
@exceptions.handle_exceptions(custom_message="Не удалось получить список расписаний")
def get_doctors_schedule(doctor_id: int,current_patient: models.Patient = Depends(oauth2.get_current_patient), db: Session = Depends(get_db)):
    """
    Получение расписания определённого доктора
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

        



@router.get("/appointments", response_model=List[schemas.AppointmentResponseToPatient])
@exceptions.handle_exceptions(custom_message="Не удалось получить все записи на прием")
def get_my_appointments(
    status_filter: Optional[str] = None,
    current_patient: models.Patient = Depends(oauth2.get_current_patient),
    db: Session = Depends(get_db)
):
    """
    Получение всех записей на прием текущего пациента по статусу записи
    """

    appointments = db.query(models.Appointment)\
        .filter(
        models.Appointment.patient_id == current_patient.id
        )
    if status_filter:
        appointments = appointments.filter(models.Appointment.status == status_filter)
    appointments = appointments.order_by(models.Appointment.id.desc()).all()
    return appointments




@router.post("/appointments/{schedule_id}", response_model=schemas.AppointmentResponseToPatient)
@exceptions.handle_exceptions(custom_message="Не удалось записаться к врачу")
def create_appointment(
    schedule_id: int,
    current_patient: models.Patient = Depends(oauth2.get_current_patient),  # Получаем пациента из токена
    db: Session = Depends(get_db)
):
    """
    Создание записи на прием к врачу.
    Пациент создает запись на себя автоматически.
    """
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

    
@router.delete("/appointments/{appointment_id}")
@exceptions.handle_exceptions(custom_message="Не удалось отменить запись")
def cancel_appointment(
    appointment_id: int,
    current_patient: models.Patient = Depends(oauth2.get_current_patient),
    db: Session = Depends(get_db)
):
    """
    Отмена записи на прием
    """

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


@router.get("/medication", response_model=dict)
@exceptions.handle_exceptions(custom_message="Не удалось получить отчёт о лекарствах пациента")
def get_patient_medication_report(
    current_patient: models.Patient = Depends(oauth2.get_current_patient),
    db: Session = Depends(get_db)
):
    """
    Отчет о лекарствах пациента и противопоказаниях.
    """
    patient_id = current_patient.id
    
    # Получаем все лекарства пациента
    patient_medicaments = db.query(models.PatientMedicament)\
        .options(joinedload(models.PatientMedicament.medicament))\
        .filter(models.PatientMedicament.patient_id == patient_id)\
        .order_by(models.PatientMedicament.start_date.desc())\
        .all()
    
    # Получаем ID лекарств пациента
    patient_medicament_ids = [pm.medicament_id for pm in patient_medicaments]
    
    # Получаем прямые противопоказания пациента к лекарствам
    patient_medicament_contraindications = db.query(models.PatientMedicamentContraindication)\
        .options(joinedload(models.PatientMedicamentContraindication.medicament))\
        .filter(models.PatientMedicamentContraindication.patient_id == patient_id)\
        .all()
    
    #Получаем другие противопоказания пациента (что нельзя делать)
    patient_other_contraindications = db.query(models.PatientOtherContraindication)\
        .options(joinedload(models.PatientOtherContraindication.contraindication))\
        .filter(models.PatientOtherContraindication.patient_id == patient_id)\
        .all()
    
    # Находим лекарства, которые нельзя принимать (на основе взаимодействий)
    forbidden_medicaments = set()
    
    # Прямые противопоказания
    for contraindication in patient_medicament_contraindications:
        forbidden_medicaments.add((
            contraindication.medicament.id,
            contraindication.medicament.name,
            "Прямое противопоказание пациента"
        ))
    
    # Взаимодействия между лекарствами пациента
    if len(patient_medicament_ids) >= 2:
        # Находим все лекарства, которые взаимодействуют с лекарствами пациента
        from sqlalchemy import or_, and_
        
        # Получаем все взаимодействия, где хотя бы одно лекарство из списка пациента
        interactions = db.query(models.MedicamentMedicamentContraindication)\
            .options(
                joinedload(models.MedicamentMedicamentContraindication.first_medicament),
                joinedload(models.MedicamentMedicamentContraindication.second_medicament)
            )\
            .filter(
                or_(
                    models.MedicamentMedicamentContraindication.medication_first_id.in_(patient_medicament_ids),
                    models.MedicamentMedicamentContraindication.medication_second_id.in_(patient_medicament_ids)
                )
            )\
            .all()
        
        # Для каждого взаимодействия определяем, какое лекарство противопоказано
        for interaction in interactions:
            # Если первое лекарство принимает пациент, то второе противопоказано
            if interaction.medication_first_id in patient_medicament_ids:
                forbidden_medicaments.add((
                    interaction.medication_second_id,
                    interaction.second_medicament.name,
                    f"Взаимодействует с '{interaction.first_medicament.name}'"
                ))
            
            # Если второе лекарство принимает пациент, то первое противопоказано
            if interaction.medication_second_id in patient_medicament_ids:
                forbidden_medicaments.add((
                    interaction.medication_first_id,
                    interaction.first_medicament.name,
                    f"Взаимодействует с '{interaction.second_medicament.name}'"
                ))
    

    current_medicament_ids = set(patient_medicament_ids)
    forbidden_medicaments_filtered = [
        {
            "medicament_id": medicament_id,
            "medicament_name": medicament_name,
            "reason": reason
        }
        for medicament_id, medicament_name, reason in forbidden_medicaments
        if medicament_id not in current_medicament_ids  # фильтруем те, что уже принимает
    ]
    
    # тчет
    report = {
        "patient_info": {
            "id": current_patient.id,
            "full_name": f"{current_patient.last_name} {current_patient.first_name} {current_patient.patronymic}",
            "birth_date": current_patient.birth_date
        },
        
        #Все лекарства пациента
        "current_medicaments": [
            {
                "id": pm.id,
                "medicament_id": pm.medicament_id,
                "medicament_name": pm.medicament.name,
                "dosage": pm.dosage,
                "frequency": pm.frequency,
                "start_date": pm.start_date,
                "end_date": pm.end_date,
                "notes": pm.notes,
                "is_active": pm.end_date is None or pm.end_date >= date.today()
            }
            for pm in patient_medicaments
        ],
        
        #Какие лекарства нельзя принимать
        "forbidden_medicaments": forbidden_medicaments_filtered,
        
        #другие противопоказания
        "forbidden_activities": [
            {
                "contraindication_id": poc.contraindication_id,
                "contraindication_name": poc.contraindication.name,
                "type": "Общее противопоказание"
            }
            for poc in patient_other_contraindications
        ]
    }
    
    return report
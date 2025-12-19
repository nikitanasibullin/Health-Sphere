import models,schemas,oauth2,utils
from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session, joinedload
from database import get_db
from typing import Optional,List
from sqlalchemy import func, and_
from sqlalchemy.exc import IntegrityError
from datetime import timedelta
from datetime import date
import exceptions 

router = APIRouter(
    prefix = "/api/doctor",
    tags=['doctor']
)

    

@router.put("/appointments/{appointment_id}", response_model=schemas.AppointmentResponse)
@exceptions.handle_exceptions(custom_message="Не удалось обновить информацию о приёме")
def update_appointment_info(
    appointment_id: int,
    update_data: schemas.AppointmentUpdate,
    current_doctor: models.Doctor = Depends(oauth2.get_current_doctor),  # ← Добавлено
    db: Session = Depends(get_db)
):
    """
    Обновление информации о записи на прием.
    """

    # Получаем запись на прием
    db_appointment = db.query(models.Appointment)\
        .filter(models.Appointment.id == appointment_id)\
        .first()
    
    if not db_appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Запись на прием с ID {appointment_id} не найдена"
        )
    
    # Проверяем, что запись относится к текущему доктору
    schedule = db.query(models.Schedule)\
        .filter(models.Schedule.id == db_appointment.schedule_id)\
        .first()
    
    if not schedule or schedule.doctor_id != current_doctor.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Эта запись не относится к вашему расписанию"
        )
    
    # Обновляем информацию
    if update_data.information is not None:
        # Добавляем подпись доктора
        info_with_signature = f"{update_data.information}\n\n— Dr. {current_doctor.last_name} {current_doctor.first_name[0]}."
        
        if db_appointment.information:
            db_appointment.information = db_appointment.information + "\n\n" + info_with_signature
        else:
            db_appointment.information = info_with_signature
    
    # Обновляем статус
    if update_data.status is not None:
        db_appointment.status = update_data.status
    
    db.commit()
    db.refresh(db_appointment)
    
    return db_appointment
        
    
@router.post("/appointments/{appointment_id}/medicaments", response_model=schemas.MedicamentsAppointmentResponse)
@exceptions.handle_exceptions(custom_message="Не удалось добавить лекарство")
def add_medicaments_for_appointment(
    appointment_id: int,
    medicaments_data: schemas.MedicamentsForAppointmentRequest,
    current_doctor: models.Doctor = Depends(oauth2.get_current_doctor),  # ← Добавлено
    db: Session = Depends(get_db)
):
    """
    Добавление лекарств пациенту..
    """

    for medicament in medicaments_data.medicaments:
        if medicament.medicament_name:
            medicament.medicament_name = medicament.medicament_name.strip().capitalize()
    # Получаем запись на прием
    db_appointment = db.query(models.Appointment)\
        .filter(models.Appointment.id == appointment_id)\
        .first()
    
    if not db_appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Запись на прием с ID {appointment_id} не найдена"
        )
    
    # Проверяем, что запись относится к текущему доктору
    schedule = db.query(models.Schedule)\
        .filter(models.Schedule.id == db_appointment.schedule_id)\
        .first()
    
    if not schedule or schedule.doctor_id != current_doctor.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Эта запись не относится к вашему расписанию"
        )
    
    # Получаем ВСЕ противопоказания пациента
    patient_contradictions = db.query(models.PatientContradiction)\
        .filter(models.PatientContradiction.patient_id == db_appointment.patient_id)\
        .all()
    
    # Получаем ВСЕ лекарства пациента
    patient_medicaments = db.query(models.PatientMedicament)\
        .filter(models.PatientMedicament.patient_id == db_appointment.patient_id)\
        .all()
    
    # Собираем ОБЩИЙ список противопоказаний пациента
    all_patient_contraindications = set()
    
    # Добавляем прямые противопоказания
    for pc in patient_contradictions:
        all_patient_contraindications.add(pc.contradiction)
    
    # Добавляем названия лекарств, которые уже принимает пациент
    for pm in patient_medicaments:
        all_patient_contraindications.add(pm.medicament_name)
    
    # Получаем противопоказания для всех лекарств пациента
    if patient_medicaments:
        patient_medicament_names = [pm.medicament_name for pm in patient_medicaments]
        
        medicament_contradictions = db.query(models.Contradiction)\
            .filter(models.Contradiction.medicament_name.in_(patient_medicament_names))\
            .all()
        
        for mc in medicament_contradictions:
            all_patient_contraindications.add(mc.contradiction)
    
    added_medicaments = []
    conflicted_medicaments = []
    
    for medicament_data in medicaments_data.medicaments:
        # ПРОВЕРКА: Является ли новое лекарство противопоказанием для пациента?
        if medicament_data.medicament_name in all_patient_contraindications:
            conflict_reasons = []
            
            # Проверяем все возможные причины
            for pc in patient_contradictions:
                if pc.contradiction == medicament_data.medicament_name:
                    conflict_reasons.append(f"Прямое противопоказание: пациент не переносит '{medicament_data.medicament_name}'")
            
            for pm in patient_medicaments:
                if pm.medicament_name == medicament_data.medicament_name:
                    conflict_reasons.append(f"Пациент уже принимает это лекарство (назначено {pm.start_date})")
            
            if patient_medicaments:
                specific_contradictions = db.query(models.Contradiction)\
                    .filter(
                        models.Contradiction.medicament_name.in_([pm.medicament_name.capitalize() for pm in patient_medicaments]),
                        models.Contradiction.contradiction == medicament_data.medicament_name
                    )\
                    .all()
                
                for sc in specific_contradictions:
                    conflict_reasons.append(f"Нельзя назначать '{medicament_data.medicament_name}' вместе с '{sc.medicament_name}'")
            
            conflicted_medicaments.append({
                "medicament_name": medicament_data.medicament_name,
                "conflict_reasons": conflict_reasons if conflict_reasons else ["Общее противопоказание"]
            })
            continue
        
        # Если проверки прошли успешно - создаем запись
        db_medicament = models.PatientMedicament(
            patient_id=db_appointment.patient_id,
            medicament_name=medicament_data.medicament_name.capitalize(),
            dosage=medicament_data.dosage,
            frequency=medicament_data.frequency,
            start_date=medicament_data.start_date,
            end_date=medicament_data.end_date,
            prescribed_by=f"Dr. {current_doctor.last_name} {current_doctor.first_name[0]}.",  # ← Используем current_doctor
            notes=medicament_data.notes
        )
        
        db.add(db_medicament)
        added_medicaments.append(db_medicament)
    
    # Если НИ ОДНО лекарство не было добавлено
    if not added_medicaments:
        error_message = "Ни одно лекарство не было добавлено из-за медицинских противопоказаний:\n"
        for conflict in conflicted_medicaments:
            error_message += f"- {conflict['medicament_name']}:\n"
            for reason in conflict['conflict_reasons']:
                error_message += f"  • {reason}\n"
        
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=error_message.strip()
        )

    # Обновляем информацию о назначении в записи приема
    medicament_names = [m.medicament_name.capitalize() for m in added_medicaments]
    info_text = f"Назначены лекарства: {', '.join(medicament_names)} (назначил: Dr. {current_doctor.last_name})"

    # Добавляем предупреждения о конфликтах, если они есть
    warning_message = None
    success_message = None
    if conflicted_medicaments:
        warning_text = "\n\nВНИМАНИЕ: Следующие лекарства не были назначены из-за противопоказаний:\n"
        for conflict in conflicted_medicaments:
            warning_text += f"- {conflict['medicament_name']}:\n"
            for reason in conflict['conflict_reasons']:
                warning_text += f"  • {reason}\n"
        info_text += warning_text
        
        warning_message = f"{len(conflicted_medicaments)} лекарств не были назначены из-за противопоказаний"
        success_message = f"Успешно добавлено {len(added_medicaments)} лекарств"
    else:
        success_message = f"Все {len(added_medicaments)} лекарств успешно добавлены"

    # Обновляем информацию в записи приема
    if db_appointment.information:
        db_appointment.information = db_appointment.information + "\n\n" + info_text
    else:
        db_appointment.information = info_text

    db.commit()

    # Обновляем объекты
    for medicament in added_medicaments:
        db.refresh(medicament)

    # Подготавливаем ответ
    response = schemas.MedicamentsAppointmentResponse(
        added_medicaments=[schemas.PatientMedicamentResponse.from_orm(m) for m in added_medicaments],
        conflicts=[
            schemas.MedicamentConflictResponse(
                medicament_name=conflict["medicament_name"],
                conflict_reasons=conflict["conflict_reasons"]
            ) for conflict in conflicted_medicaments
        ],
        warning=warning_message,
        message=success_message
    )
    
    return response


@router.put("/appointments/{appointment_id}/medicaments", response_model=schemas.MedicamentsAppointmentResponse)
@exceptions.handle_exceptions(custom_message="Не удалось добавить лекарство")
def add_medicaments_for_appointment(
    appointment_id: int,
    medicaments_data: schemas.MedicamentsForAppointmentRequest,
    current_doctor: models.Doctor = Depends(oauth2.get_current_doctor),  # ← Добавлено
    db: Session = Depends(get_db)
):
    """
    Добавление лекарств пациенту..
    """

    for medicament in medicaments_data.medicaments:
        if medicament.medicament_name:
            medicament.medicament_name = medicament.medicament_name.strip().capitalize()
    # Получаем запись на прием
    db_appointment = db.query(models.Appointment)\
        .filter(models.Appointment.id == appointment_id)\
        .first()
    
    if not db_appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Запись на прием с ID {appointment_id} не найдена"
        )
    
    # Проверяем, что запись относится к текущему доктору
    schedule = db.query(models.Schedule)\
        .filter(models.Schedule.id == db_appointment.schedule_id)\
        .first()
    
    if not schedule or schedule.doctor_id != current_doctor.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Эта запись не относится к вашему расписанию"
        )
    
    # Получаем ВСЕ противопоказания пациента
    patient_contradictions = db.query(models.PatientContradiction)\
        .filter(models.PatientContradiction.patient_id == db_appointment.patient_id)\
        .all()
    
    # Получаем ВСЕ лекарства пациента
    patient_medicaments = db.query(models.PatientMedicament)\
        .filter(models.PatientMedicament.patient_id == db_appointment.patient_id)\
        .all()
    
    # Собираем ОБЩИЙ список противопоказаний пациента
    all_patient_contraindications = set()
    
    # Добавляем прямые противопоказания
    for pc in patient_contradictions:
        all_patient_contraindications.add(pc.contradiction)
    
    # Добавляем названия лекарств, которые уже принимает пациент
    for pm in patient_medicaments:
        all_patient_contraindications.add(pm.medicament_name)
    
    # Получаем противопоказания для всех лекарств пациента
    if patient_medicaments:
        patient_medicament_names = [pm.medicament_name for pm in patient_medicaments]
        
        medicament_contradictions = db.query(models.Contradiction)\
            .filter(models.Contradiction.medicament_name.in_(patient_medicament_names))\
            .all()
        
        for mc in medicament_contradictions:
            all_patient_contraindications.add(mc.contradiction)
    
    added_medicaments = []
    conflicted_medicaments = []
    
    for medicament_data in medicaments_data.medicaments:
        # ПРОВЕРКА: Является ли новое лекарство противопоказанием для пациента?
        if medicament_data.medicament_name in all_patient_contraindications:
            conflict_reasons = []
            
            # Проверяем все возможные причины
            for pc in patient_contradictions:
                if pc.contradiction == medicament_data.medicament_name:
                    conflict_reasons.append(f"Прямое противопоказание: пациент не переносит '{medicament_data.medicament_name}'")
            
            for pm in patient_medicaments:
                if pm.medicament_name == medicament_data.medicament_name:
                    conflict_reasons.append(f"Пациент уже принимает это лекарство (назначено {pm.start_date})")
            
            if patient_medicaments:
                specific_contradictions = db.query(models.Contradiction)\
                    .filter(
                        models.Contradiction.medicament_name.in_([pm.medicament_name.capitalize() for pm in patient_medicaments]),
                        models.Contradiction.contradiction == medicament_data.medicament_name
                    )\
                    .all()
                
                for sc in specific_contradictions:
                    conflict_reasons.append(f"Нельзя назначать '{medicament_data.medicament_name}' вместе с '{sc.medicament_name}'")
            
            conflicted_medicaments.append({
                "medicament_name": medicament_data.medicament_name,
                "conflict_reasons": conflict_reasons if conflict_reasons else ["Общее противопоказание"]
            })
            continue
        
        # Если проверки прошли успешно - создаем запись
        db_medicament = models.PatientMedicament(
            patient_id=db_appointment.patient_id,
            medicament_name=medicament_data.medicament_name.capitalize(),
            dosage=medicament_data.dosage,
            frequency=medicament_data.frequency,
            start_date=medicament_data.start_date,
            end_date=medicament_data.end_date,
            prescribed_by=f"Dr. {current_doctor.last_name} {current_doctor.first_name[0]}.",  # ← Используем current_doctor
            notes=medicament_data.notes
        )
        
        db.add(db_medicament)
        added_medicaments.append(db_medicament)
    
    # Если НИ ОДНО лекарство не было добавлено
    if not added_medicaments:
        error_message = "Ни одно лекарство не было добавлено из-за медицинских противопоказаний:\n"
        for conflict in conflicted_medicaments:
            error_message += f"- {conflict['medicament_name']}:\n"
            for reason in conflict['conflict_reasons']:
                error_message += f"  • {reason}\n"
        
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=error_message.strip()
        )

    # Обновляем информацию о назначении в записи приема
    medicament_names = [m.medicament_name.capitalize() for m in added_medicaments]
    info_text = f"Назначены лекарства: {', '.join(medicament_names)} (назначил: Dr. {current_doctor.last_name})"

    # Добавляем предупреждения о конфликтах, если они есть
    warning_message = None
    success_message = None
    if conflicted_medicaments:
        warning_text = "\n\nВНИМАНИЕ: Следующие лекарства не были назначены из-за противопоказаний:\n"
        for conflict in conflicted_medicaments:
            warning_text += f"- {conflict['medicament_name']}:\n"
            for reason in conflict['conflict_reasons']:
                warning_text += f"  • {reason}\n"
        info_text += warning_text
        
        warning_message = f"{len(conflicted_medicaments)} лекарств не были назначены из-за противопоказаний"
        success_message = f"Успешно добавлено {len(added_medicaments)} лекарств"
    else:
        success_message = f"Все {len(added_medicaments)} лекарств успешно добавлены"

    # Обновляем информацию в записи приема
    if db_appointment.information:
        db_appointment.information = db_appointment.information + "\n\n" + info_text
    else:
        db_appointment.information = info_text

    db.commit()

    # Обновляем объекты
    for medicament in added_medicaments:
        db.refresh(medicament)

    # Подготавливаем ответ
    response = schemas.MedicamentsAppointmentResponse(
        added_medicaments=[schemas.PatientMedicamentResponse.from_orm(m) for m in added_medicaments],
        conflicts=[
            schemas.MedicamentConflictResponse(
                medicament_name=conflict["medicament_name"],
                conflict_reasons=conflict["conflict_reasons"]
            ) for conflict in conflicted_medicaments
        ],
        warning=warning_message,
        message=success_message
    )
    
    return response

    
# Получение всех записей на прием к текущему доктору
@router.get("/appointments", response_model=List[schemas.AppointmentResponse])
@exceptions.handle_exceptions(custom_message="Не удалось получить все записи на прием")
def get_my_appointments(
    status_filter: Optional[str] = None,
    current_doctor: models.Patient = Depends(oauth2.get_current_doctor),
    db: Session = Depends(get_db)
):
    """
    Получение всех записей на прием текущего доктора
    """

    appointments = db.query(models.Appointment)\
         .join(models.Appointment.schedule)\
         .filter(models.Schedule.doctor_id == current_doctor.id)
    if status_filter:
        appointments = appointments.filter(models.Appointment.status == status_filter)
    appointments = appointments.order_by(models.Appointment.id.desc()).all()
    return appointments






@router.get("/patients/{patient_id}/medicaments", response_model=List[schemas.PatientMedicamentResponse])
@exceptions.handle_exceptions(custom_message="Не удалось получить все лекарства пациента")
def get_patient_medicaments(
    patient_id: int,
    current_doctor: models.Doctor = Depends(oauth2.get_current_doctor),
    db: Session = Depends(get_db)
):
    """
    Получение всех лекарств пациента.
    Доктор может просматривать лекарства любого пациента.
    """
    # Проверяем существование пациента
    patient = db.query(models.Patient)\
        .filter(models.Patient.id == patient_id)\
        .first()
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Пациент с ID {patient_id} не найден"
        )
    
    # Получаем все лекарства пациента
    medicaments = db.query(models.PatientMedicament)\
        .filter(models.PatientMedicament.patient_id == patient_id)\
        .order_by(
            models.PatientMedicament.start_date.desc(),
            models.PatientMedicament.medicament_name.asc()
        )\
        .all()
    
    return medicaments
    

    
@router.get("/patients/{patient_id}/medicaments/active", response_model=List[schemas.PatientMedicamentResponse])
@exceptions.handle_exceptions(custom_message="Не удалось получить активные лекарства пациента")
def get_patient_active_medicaments(
    patient_id: int,
    current_doctor: models.Doctor = Depends(oauth2.get_current_doctor),
    db: Session = Depends(get_db)
):
    """
    Получение только активных лекарств пациента.
    """
    patient = db.query(models.Patient)\
        .filter(models.Patient.id == patient_id)\
        .first()
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Пациент с ID {patient_id} не найден"
        )
    
    # Получаем активные лекарства
    active_medicaments = db.query(models.PatientMedicament)\
        .filter(models.PatientMedicament.patient_id == patient_id)\
        .filter(
            (models.PatientMedicament.end_date.is_(None)) |
            (models.PatientMedicament.end_date >= date.today())
        )\
        .order_by(models.PatientMedicament.start_date.desc())\
        .all()
    
    return active_medicaments


@router.post("/patients/{patient_id}/contraindications", response_model=dict)
@exceptions.handle_exceptions(custom_message="Не удалось добавить противопоказания пациенту")
def add_patient_contradictions(
    patient_id: int,
    request_data: schemas.PatientContraindicationsRequest,
    current_doctor: models.Doctor = Depends(oauth2.get_current_doctor),
    db: Session = Depends(get_db)
):
    """
    Добавление противопоказаний пациенту.
    Доктор может добавлять противопоказания любому пациенту.
    """
    # Проверяем существование пациента
    patient = db.query(models.Patient)\
        .filter(models.Patient.id == patient_id)\
        .first()
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Пациент с ID {patient_id} не найден"
        )
    
    contradictions = [name.capitalize() for name in request_data.contradictions]
    added_count = 0
    already_exist = []
    
    for contradiction in contradictions:
        # Проверяем, существует ли уже такое противопоказание для пациента
        existing = db.query(models.PatientContradiction)\
            .filter(
                and_(
                    models.PatientContradiction.patient_id == patient_id,
                    models.PatientContradiction.contradiction == contradiction
                )
            )\
            .first()
        
        if existing:
            already_exist.append(contradiction)
            continue
        
        # Создаем новое противопоказание
        db_contradiction = models.PatientContradiction(
            patient_id=patient_id,
            contradiction=contradiction
        )
        
        db.add(db_contradiction)
        added_count += 1
    
    if added_count > 0 or already_exist:
        db.commit()
        
        response = {
            "status": "success",
            "message": f"Обработка противопоказаний пациента завершена",
            "patient_id": patient_id,
            "patient_name": f"{patient.last_name} {patient.first_name}",
            "added_by_doctor": f"Dr. {current_doctor.last_name}"
        }
        
        if added_count > 0:
            response["added_count"] = added_count
            response["added_contradictions"] = [c for c in contradictions if c not in already_exist]
        
        if already_exist:
            response["already_exist"] = already_exist
        
        return response
    else:
        return {
            "status": "info",
            "message": "Нет противопоказаний для добавления",
            "patient_id": patient_id
        }
            


@router.get("/medicaments", response_model=List[dict])
@exceptions.handle_exceptions(custom_message="Не удалось получить список медикаментов")
def get_all_medicaments(
    current_doctor: models.Doctor = Depends(oauth2.get_current_doctor),
    db: Session = Depends(get_db)
):
    """
    Получить все медикаменты из справочника
    """
    medicaments = db.query(models.Medicament).order_by(models.Medicament.name).all()
    
    return [
        {
            "id": m.id,
            "name": m.name
        }
        for m in medicaments
    ]


@router.post("/medicaments", response_model=dict)
@exceptions.handle_exceptions(custom_message="Не удалось добавить медикамент")
def add_medicament(
    medicament_data: dict,  # или создайте схему schemas.MedicamentCreate
    current_doctor: models.Doctor = Depends(oauth2.get_current_doctor),
    db: Session = Depends(get_db)
):
    """
    Добавить новый медикамент в справочник
    """
    # Проверяем, нет ли уже такого медикамента
    existing = db.query(models.Medicament)\
        .filter(models.Medicament.name == medicament_data["name"])\
        .first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Медикамент с таким названием уже существует"
        )
    
    # Создаем новый медикамент
    new_medicament = models.Medicament(
        name=medicament_data["name"].capitalize()
    )
    
    db.add(new_medicament)
    db.commit()
    db.refresh(new_medicament)
    
    return {
        "id": new_medicament.id,
        "name": new_medicament.name,
        "message": "Медикамент успешно добавлен"
    }



@router.delete("/medicaments/{medicament_id}", response_model=dict)
@exceptions.handle_exceptions(custom_message="Не удалось удалить медикамент")
def delete_medicament(
    medicament_id: int,
    current_doctor: models.Doctor = Depends(oauth2.get_current_doctor),
    db: Session = Depends(get_db)
):
    """
    Удалить медикамент из справочника
    """
    medicament = db.query(models.Medicament)\
        .filter(models.Medicament.id == medicament_id)\
        .first()
    
    if not medicament:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Медикамент не найден"
        )
    
    db.delete(medicament)
    db.commit()
    
    return {
        "message": f"Медикамент '{medicament.name}' успешно удален",
        "deleted_id": medicament_id
    }



@router.get("/contraindications", response_model=List[dict])
@exceptions.handle_exceptions(custom_message="Не удалось получить список противопоказаний")
def get_all_contraindications(
    current_doctor: models.Doctor = Depends(oauth2.get_current_doctor),
    db: Session = Depends(get_db)
):
    """
    Получить все противопоказания из справочника
    """
    contraindications = db.query(models.OtherContraindication)\
        .order_by(models.OtherContraindication.name)\
        .all()
    
    return [
        {
            "id": c.id,
            "name": c.name
        }
        for c in contraindications
    ]



@router.post("/contraindications", response_model=dict)
@exceptions.handle_exceptions(custom_message="Не удалось добавить противопоказание")
def add_contraindication(
    contraindication_data: dict,
    current_doctor: models.Doctor = Depends(oauth2.get_current_doctor),
    db: Session = Depends(get_db)
):
    """
    Добавить новое противопоказание в справочник
    """
    existing = db.query(models.OtherContraindication)\
        .filter(models.OtherContraindication.name == contraindication_data["name"])\
        .first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Противопоказание с таким названием уже существует"
        )
    
    new_contraindication = models.OtherContraindication(
        name=contraindication_data["name"].capitalize()
    )
    
    db.add(new_contraindication)
    db.commit()
    db.refresh(new_contraindication)
    
    return {
        "id": new_contraindication.id,
        "name": new_contraindication.name,
        "message": "Противопоказание успешно добавлено"
    }


@router.delete("/contraindications/{contraindication_id}", response_model=dict)
@exceptions.handle_exceptions(custom_message="Не удалось удалить противопоказание")
def delete_contraindication(
    contraindication_id: int,
    current_doctor: models.Doctor = Depends(oauth2.get_current_doctor),
    db: Session = Depends(get_db)
):
    """
    Удалить противопоказание из справочника
    """
    contraindication = db.query(models.OtherContraindication)\
        .filter(models.OtherContraindication.id == contraindication_id)\
        .first()
    
    
    if not contraindication:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Противопоказание не найден"
        )
    
    db.delete(contraindication)
    db.commit()
    
    return {
        "message": f"Противопоказание '{contraindication.name}' успешно удалено",
        "deleted_id": contraindication_id
    }



@router.get("/interactions", response_model=List[dict])
@exceptions.handle_exceptions(custom_message="Не удалось получить взаимодействия медикаментов")
def get_all_medicament_interactions(
    current_doctor: models.Doctor = Depends(oauth2.get_current_doctor),
    db: Session = Depends(get_db)
):
    """
    Получить все взаимодействия между медикаментами
    """
    from sqlalchemy.orm import aliased
    
    # Создаем алиасы для таблицы medicaments
    Medicament1 = aliased(models.Medicament)
    Medicament2 = aliased(models.Medicament)
    
    # Делаем join с таблицей medicaments дважды
    interactions = db.query(
        models.MedicamentMedicamentContraindication,
        Medicament1,
        Medicament2
    )\
    .join(Medicament1, models.MedicamentMedicamentContraindication.medication_first_id == Medicament1.id)\
    .join(Medicament2, models.MedicamentMedicamentContraindication.medication_second_id == Medicament2.id)\
    .all()
    
    return [
        {
            "first_medicament_id": interaction.medication_first_id,
            "first_medicament_name": medicament1.name if medicament1 else "Неизвестно",
            "second_medicament_id": interaction.medication_second_id,
            "second_medicament_name": medicament2.name if medicament2 else "Неизвестно"
        }
        for interaction, medicament1, medicament2 in interactions
    ]


@router.post("/interactions", response_model=dict)
@exceptions.handle_exceptions(custom_message="Не удалось добавить взаимодействие")
def add_medicament_interaction(
    interaction_data: dict,  # {"first_medicament_id": 1, "second_medicament_id": 2}
    current_doctor: models.Doctor = Depends(oauth2.get_current_doctor),
    db: Session = Depends(get_db)
):
    """
    Добавить противопоказанное взаимодействие между медикаментами
    """
    # Упорядочиваем ID (меньший первый)
    id1, id2 = sorted([interaction_data["first_medicament_id"], 
                       interaction_data["second_medicament_id"]])
    
    # Проверяем существование медикаментов
    medicament1 = db.query(models.Medicament).filter(models.Medicament.id == id1).first()
    medicament2 = db.query(models.Medicament).filter(models.Medicament.id == id2).first()
    
    if not medicament1 or not medicament2:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Один или оба медикамента не найдены"
        )
    
    # Проверяем, нет ли уже такого взаимодействия
    existing = db.query(models.MedicamentMedicamentContraindication)\
        .filter(
            models.MedicamentMedicamentContraindication.medication_first_id == id1,
            models.MedicamentMedicamentContraindication.medication_second_id == id2
        )\
        .first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Такое взаимодействие уже существует"
        )
    
    # Создаем взаимодействие
    new_interaction = models.MedicamentMedicamentContraindication(
        medication_first_id=id1,
        medication_second_id=id2
    )
    
    db.add(new_interaction)
    db.commit()
    
    return {
        "message": f"Взаимодействие между '{medicament1.name}' и '{medicament2.name}' добавлено",
        "first_medicament_id": id1,
        "second_medicament_id": id2
    }

@router.post("/medication-contraindication", response_model=dict)
@exceptions.handle_exceptions(custom_message="Не удалось добавить связь медикамент-противопоказание")
def add_medicament_contraindication_link(
    link_data: dict,
    current_doctor: models.Doctor = Depends(oauth2.get_current_doctor),
    db: Session = Depends(get_db)
):
    """
    Добавить связь между медикаментом и противопоказанием
    """
    medicament_id = link_data.get("medicament_id")
    contraindication_id = link_data.get("contraindication_id")
    
    if not medicament_id or not contraindication_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Необходимо указать medicament_id и contraindication_id"
        )
    
    # Проверяем существование медикамента
    medicament = db.query(models.Medicament)\
        .filter(models.Medicament.id == medicament_id)\
        .first()
    
    if not medicament:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Медикамент не найден"
        )
    
    # Проверяем существование противопоказания
    contraindication = db.query(models.OtherContraindication)\
        .filter(models.OtherContraindication.id == contraindication_id)\
        .first()
    
    if not contraindication:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Противопоказание не найдено"
        )
    
    # Проверяем, нет ли уже такой связи
    existing = db.query(models.MedicationContraindicationOther)\
        .filter(
            models.MedicationContraindicationOther.medicament_id == medicament_id,
            models.MedicationContraindicationOther.contraindication_id == contraindication_id
        )\
        .first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Такая связь уже существует"
        )
    
    # Создаем связь
    new_link = models.MedicationContraindicationOther(
        medicament_id=medicament_id,
        contraindication_id=contraindication_id
    )
    
    db.add(new_link)
    db.commit()
    
    return {
        "message": f"Противопоказание добавлено: '{medicament.name}' - '{contraindication.name}'",
        "medicament_id": medicament_id,
        "contraindication_id": contraindication_id,
        "medicament_name": medicament.name,
        "contraindication_name": contraindication.name
    }

@router.get("/medication-contraindication", response_model=List[dict])
@exceptions.handle_exceptions(custom_message="Не удалось получить все связи медикамент-противопоказание")
def get_all_medication_contraindications(
    current_doctor: models.Doctor = Depends(oauth2.get_current_doctor),
    db: Session = Depends(get_db)
):
    """
    Получить все связи между медикаментами и противопоказаниями
    """
    # Делаем join с таблицами medicaments и other_contraindications
    results = db.query(
        models.MedicationContraindicationOther,
        models.Medicament,
        models.OtherContraindication
    )\
    .join(models.Medicament, models.MedicationContraindicationOther.medicament_id == models.Medicament.id)\
    .join(models.OtherContraindication, models.MedicationContraindicationOther.contraindication_id == models.OtherContraindication.id)\
    .all()
    
    return [
        {
            "medicament_id": medicament.id,
            "medicament_name": medicament.name if medicament else "Неизвестно",
            "contraindication_id": contraindication.id,
            "contraindication_name": contraindication.name if contraindication else "Неизвестно"
        }
        for link, medicament, contraindication in results
    ]


@router.delete("/interactions", response_model=dict)
@exceptions.handle_exceptions(custom_message="Не удалось удалить взаимодействие медикаментов")
def remove_medicament_interaction(
    interaction_data: dict,  # {"medicament1_id": 1, "medicament2_id": 2}
    current_doctor: models.Doctor = Depends(oauth2.get_current_doctor),
    db: Session = Depends(get_db)
):
    """
    Удалить взаимодействие между двумя медикаментами
    Принимает JSON: {"medicament1_id": 1, "medicament2_id": 2}
    """
    medicament1_id = interaction_data.get("medicament1_id")
    medicament2_id = interaction_data.get("medicament2_id")
    
    if not medicament1_id or not medicament2_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Необходимо указать medicament1_id и medicament2_id"
        )
    
    # Упорядочиваем ID (меньший первый)
    id1, id2 = sorted([medicament1_id, medicament2_id])
    
    # Ищем взаимодействие
    interaction = db.query(models.MedicamentMedicamentContraindication)\
        .filter(
            models.MedicamentMedicamentContraindication.medication_first_id == id1,
            models.MedicamentMedicamentContraindication.medication_second_id == id2
        )\
        .first()
    
    if not interaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Взаимодействие не найдено"
        )
    
    # Получаем названия для сообщения
    medicament1 = db.query(models.Medicament).filter(models.Medicament.id == medicament1_id).first()
    medicament2 = db.query(models.Medicament).filter(models.Medicament.id == medicament2_id).first()
    
    db.delete(interaction)
    db.commit()
    
    return {
        "message": f"Взаимодействие удалено: '{medicament1.name if medicament1 else 'Неизвестно'}' и '{medicament2.name if medicament2 else 'Неизвестно'}'",
        "medicament1_id": medicament1_id,
        "medicament2_id": medicament2_id
    }




@router.delete("/medication-contraindication", response_model=dict)
@exceptions.handle_exceptions(custom_message="Не удалось удалить связь медикамент-противопоказание")
def remove_medicament_contraindication_link(
    link_data: dict,  # {"medicament_id": 1, "contraindication_id": 2}
    current_doctor: models.Doctor = Depends(oauth2.get_current_doctor),
    db: Session = Depends(get_db)
):
    """
    Удалить связь между медикаментом и противопоказанием
    Принимает JSON: {"medicament_id": 1, "contraindication_id": 2}
    """
    medicament_id = link_data.get("medicament_id")
    contraindication_id = link_data.get("contraindication_id")
    
    if not medicament_id or not contraindication_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Необходимо указать medicament_id и contraindication_id"
        )
    
    # Ищем связь
    link = db.query(models.MedicationContraindicationOther)\
        .filter(
            models.MedicationContraindicationOther.medicament_id == medicament_id,
            models.MedicationContraindicationOther.contraindication_id == contraindication_id
        )\
        .first()
    
    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Связь не найдена"
        )
    
    # Получаем названия для сообщения
    medicament = db.query(models.Medicament).filter(models.Medicament.id == medicament_id).first()
    contraindication = db.query(models.OtherContraindication)\
        .filter(models.OtherContraindication.id == contraindication_id)\
        .first()
    
    db.delete(link)
    db.commit()
    
    return {
        "message": f"Связь удалена: '{medicament.name if medicament else 'Неизвестно'}' - '{contraindication.name if contraindication else 'Неизвестно'}'",
        "medicament_id": medicament_id,
        "contraindication_id": contraindication_id
    }




@router.get("/medicaments/{medicament_id}/all-contraindications", response_model=dict)
@exceptions.handle_exceptions(custom_message="Не удалось получить все противопоказания медикамента")
def get_all_medicament_contraindications(
    medicament_id: int,
    current_doctor: models.Doctor = Depends(oauth2.get_current_doctor),
    db: Session = Depends(get_db)
):
    """
    Получить ВСЕ противопоказания для конкретного медикамента:
    1. Взаимодействия с другими медикаментами
    2. Другие противопоказания (аллергии, заболевания и т.д.)
    """
    # Проверяем существование медикамента
    medicament = db.query(models.Medicament)\
        .filter(models.Medicament.id == medicament_id)\
        .first()
    
    if not medicament:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Медикамент не найден"
        )
    
    # 1. Получаем взаимодействия с другими медикаментами
    medicament_interactions = db.query(models.MedicamentMedicamentContraindication)\
        .options(
            joinedload(models.MedicamentMedicamentContraindication.first_medicament),
            joinedload(models.MedicamentMedicamentContraindication.second_medicament)
        )\
        .filter(
            (models.MedicamentMedicamentContraindication.medication_first_id == medicament_id) |
            (models.MedicamentMedicamentContraindication.medication_second_id == medicament_id)
        )\
        .all()
    
    # 2. Получаем другие противопоказания медикамента
    other_contraindications = db.query(models.MedicationContraindicationOther)\
        .options(
            joinedload(models.MedicationContraindicationOther.contraindication)
        )\
        .filter(models.MedicationContraindicationOther.medicament_id == medicament_id)\
        .all()
    
    # Формируем ответ
    response = {
        "medicament": {
            "id": medicament.id,
            "name": medicament.name
        },
        "contraindications": {
            "medicament_interactions": [
                {
                    "id": f"{mi.medication_first_id}_{mi.medication_second_id}",
                    "contraindicated_medicament": {
                        "id": (
                            mi.second_medicament.id 
                            if mi.medication_first_id == medicament_id 
                            else mi.first_medicament.id
                        ),
                        "name": (
                            mi.second_medicament.name 
                            if mi.medication_first_id == medicament_id 
                            else mi.first_medicament.name
                        ) if (mi.first_medicament and mi.second_medicament) else "Неизвестно"
                    },
                    "interaction_type": "медикамент-медикамент"
                }
                for mi in medicament_interactions
            ],
            "other_contraindications": [
                {
                    "id": oc.contraindication_id,
                    "name": oc.contraindication.name if oc.contraindication else "Неизвестно",
                    "type": "другое_противопоказание"
                }
                for oc in other_contraindications
            ]
        },
        "summary": {
            "total_medicament_interactions": len(medicament_interactions),
            "total_other_contraindications": len(other_contraindications),
            "total_contraindications": len(medicament_interactions) + len(other_contraindications)
        }
    }
    
    return response



@router.post("/patient/medication-contraindication", response_model=dict)
@exceptions.handle_exceptions(custom_message="Не удалось добавить противопоказание пациента")
def add_patient_medication_contraindication(
    data: dict,  # {"patient_id": 1, "medicament_id": 2}
    current_doctor: models.Doctor = Depends(oauth2.get_current_doctor),
    db: Session = Depends(get_db)
):
    """
    Добавить противопоказание пациента к медикаменту
    Принимает JSON: {"patient_id": 1, "medicament_id": 2}
    """
    patient_id = data.get("patient_id")
    medicament_id = data.get("medicament_id")
    
    if not patient_id or not medicament_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Необходимо указать patient_id и medicament_id"
        )
    
    # Проверяем существование пациента
    patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пациент не найден"
        )
    
    # Проверяем существование медикамента
    medicament = db.query(models.Medicament).filter(models.Medicament.id == medicament_id).first()
    if not medicament:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Медикамент не найден"
        )
    
    # Проверяем, нет ли уже такой записи
    existing = db.query(models.PatientMedicamentContraindication)\
        .filter(
            models.PatientMedicamentContraindication.patient_id == patient_id,
            models.PatientMedicamentContraindication.medicament_id == medicament_id
        )\
        .first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Такое противопоказание уже существует у пациента"
        )
    
    # Создаем запись
    new_record = models.PatientMedicamentContraindication(
        patient_id=patient_id,
        medicament_id=medicament_id
    )
    
    db.add(new_record)
    db.commit()
    
    return {
        "message": f"Добавлено противопоказание: пациент '{patient.id}' не может принимать '{medicament.name}'",
        "patient_id": patient_id,
        "medicament_id": medicament_id
    }

@router.get("/patient/medication-contraindication/{patient_id}", response_model=List[dict])
@exceptions.handle_exceptions(custom_message="Не удалось получить противопоказания пациента")
def get_patient_medication_contraindications(
    patient_id: int,
    current_doctor: models.Doctor = Depends(oauth2.get_current_doctor),
    db: Session = Depends(get_db)
):
    """
    Получить все противопоказания пациента к медикаментам
    """
    # Делаем join с таблицами patient и medicament
    results = db.query(
        models.PatientMedicamentContraindication,
        models.Patient,
        models.Medicament
    )\
    .join(models.Patient, models.PatientMedicamentContraindication.patient_id == models.Patient.id)\
    .join(models.Medicament, models.PatientMedicamentContraindication.medicament_id == models.Medicament.id)\
    .filter(models.PatientMedicamentContraindication.patient_id == patient_id)\
    .all()
    
    return [
        {
            "patient_id": patient.id,
            "patient_name": patient.first_name,
            "medicament_id": medicament.id,
            "medicament_name": medicament.name,
        }
        for record, patient, medicament in results
    ]


@router.delete("/patient/medication-contraindication", response_model=dict)
@exceptions.handle_exceptions(custom_message="Не удалось удалить противопоказание пациента")
def remove_patient_medication_contraindication(
    data: dict,  # {"patient_id": 1, "medicament_id": 2}
    current_doctor: models.Doctor = Depends(oauth2.get_current_doctor),
    db: Session = Depends(get_db)
):
    """
    Удалить противопоказание пациента к медикаменту
    Принимает JSON: {"patient_id": 1, "medicament_id": 2}
    """
    patient_id = data.get("patient_id")
    medicament_id = data.get("medicament_id")
    
    if not patient_id or not medicament_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Необходимо указать patient_id и medicament_id"
        )
    
    # Ищем запись
    record = db.query(models.PatientMedicamentContraindication)\
        .filter(
            models.PatientMedicamentContraindication.patient_id == patient_id,
            models.PatientMedicamentContraindication.medicament_id == medicament_id
        )\
        .first()
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Противопоказание не найдено"
        )
    
    # Получаем названия для сообщения
    patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    medicament = db.query(models.Medicament).filter(models.Medicament.id == medicament_id).first()
    
    db.delete(record)
    db.commit()
    
    return {
        "message": f"Удалено противопоказание: пациент '{patient.first_name}' может принимать '{medicament.name}'",
        "patient_id": patient_id,
        "medicament_id": medicament_id
    }



@router.post("/patient/other-contraindication", response_model=dict)
@exceptions.handle_exceptions(custom_message="Не удалось добавить общее противопоказание пациента")
def add_patient_other_contraindication(
    data: dict,  # {"patient_id": 1, "contraindication_id": 2}
    current_doctor: models.Doctor = Depends(oauth2.get_current_doctor),
    db: Session = Depends(get_db)
):
    """
    Добавить общее противопоказание пациента
    Принимает JSON: {"patient_id": 1, "contraindication_id": 2}
    """
    patient_id = data.get("patient_id")
    contraindication_id = data.get("contraindication_id")
    
    if not patient_id or not contraindication_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Необходимо указать patient_id и contraindication_id"
        )
    
    # Проверяем существование пациента
    patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пациент не найден"
        )
    
    # Проверяем существование противопоказания
    contraindication = db.query(models.OtherContraindication)\
        .filter(models.OtherContraindication.id == contraindication_id)\
        .first()
    
    if not contraindication:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Противопоказание не найдено"
        )
    
    # Проверяем, нет ли уже такой записи
    existing = db.query(models.PatientOtherContraindication)\
        .filter(
            models.PatientOtherContraindication.patient_id == patient_id,
            models.PatientOtherContraindication.contraindication_id == contraindication_id
        )\
        .first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Такое противопоказание уже существует у пациента"
        )
    
    # Создаем запись
    new_record = models.PatientOtherContraindication(
        patient_id=patient_id,
        contraindication_id=contraindication_id
    )
    
    db.add(new_record)
    db.commit()
    
    return {
        "message": f"Добавлено противопоказание: пациент '{patient.id}' имеет противопоказание: '{contraindication.name}'",
        "patient_id": patient_id,
        "contraindication_id": contraindication_id
    }


@router.get("/patient/other-contraindication/{patient_id}", response_model=List[dict])
@exceptions.handle_exceptions(custom_message="Не удалось получить общие противопоказания пациента")
def get_patient_other_contraindications(
    patient_id: int,
    current_doctor: models.Doctor = Depends(oauth2.get_current_doctor),
    db: Session = Depends(get_db)
):
    """
    Получить все общие противопоказания пациента
    """
    # Делаем join с таблицами patient и other_contraindication
    results = db.query(
        models.PatientOtherContraindication,
        models.Patient,
        models.OtherContraindication
    )\
    .join(models.Patient, models.PatientOtherContraindication.patient_id == models.Patient.id)\
    .join(models.OtherContraindication, models.PatientOtherContraindication.contraindication_id == models.OtherContraindication.id)\
    .filter(models.PatientOtherContraindication.patient_id == patient_id)\
    .all()
    
    return [
        {
            "patient_id": patient.id,
            "patient_name": patient.first_name,
            "contraindication_id": contraindication.id,
            "contraindication_name": contraindication.name,
        }
        for record, patient, contraindication in results
    ]


@router.delete("/patient/other-contraindication", response_model=dict)
@exceptions.handle_exceptions(custom_message="Не удалось удалить общее противопоказание пациента")
def remove_patient_other_contraindication(
    data: dict,  # {"patient_id": 1, "contraindication_id": 2}
    current_doctor: models.Doctor = Depends(oauth2.get_current_doctor),
    db: Session = Depends(get_db)
):
    """
    Удалить общее противопоказание пациента
    Принимает JSON: {"patient_id": 1, "contraindication_id": 2}
    """
    patient_id = data.get("patient_id")
    contraindication_id = data.get("contraindication_id")
    
    if not patient_id or not contraindication_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Необходимо указать patient_id и contraindication_id"
        )
    
    # Ищем запись
    record = db.query(models.PatientOtherContraindication)\
        .filter(
            models.PatientOtherContraindication.patient_id == patient_id,
            models.PatientOtherContraindication.contraindication_id == contraindication_id
        )\
        .first()
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Противопоказание не найдено"
        )
    
    # Получаем названия для сообщения
    patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    contraindication = db.query(models.OtherContraindication)\
        .filter(models.OtherContraindication.id == contraindication_id)\
        .first()
    
    db.delete(record)
    db.commit()
    
    return {
        "message": f"Удалено противопоказание: пациент '{patient.first_name}' не имеет '{contraindication.name}'",
        "patient_id": patient_id,
        "contraindication_id": contraindication_id
    }
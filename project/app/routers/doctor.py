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
from sqlalchemy import and_, or_

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

    
    # Обновляем статус
    if update_data.status is not None:
        db_appointment.status = update_data.status
        db_appointment.information=update_data.information
    
    db.commit()
    db.refresh(db_appointment)
    
    return db_appointment
        
    
@router.post("/appointments/{appointment_id}/medicaments", response_model=schemas.MedicamentsAppointmentResponse)
@exceptions.handle_exceptions(custom_message="Не удалось добавить лекарство")
def add_medicaments_for_appointment(
    appointment_id: int,
    medicaments_data: schemas.MedicamentsForAppointmentRequest,
    current_doctor: models.Doctor = Depends(oauth2.get_current_doctor),
    db: Session = Depends(get_db)
):
    """
    Добавление лекарств пациенту с проверкой медицинских противопоказаний.
    Проверяются только:
    1. Прямые противопоказания пациента к лекарствам (PatientMedicamentContraindication)
    2. Взаимодействия между лекарствами (MedicamentMedicamentContraindication)
    """
    from datetime import date

    # Получаем запись на прием
    db_appointment = db.query(models.Appointment)\
        .filter(models.Appointment.id == appointment_id)\
        .first()
    
    if not db_appointment: 
        raise HTTPException(
            status_code=404,
            detail=f"Запись на прием с ID {appointment_id} не найдена"
        )
    
    # Проверяем, что запись относится к текущему доктору
    schedule = db.query(models.Schedule)\
        .filter(models.Schedule.id == db_appointment.schedule_id)\
        .first()
    
    if not schedule or schedule.doctor_id != current_doctor.id:
        raise HTTPException(
            status_code=403,
            detail="Эта запись не относится к вашему расписанию"
        )
    
    patient_id = db_appointment.patient_id
    today = date.today()
    
    #Получаем только act. лекарства пациента
    
    patient_active_medicaments = db.query(models.PatientMedicament)\
        .filter(models.PatientMedicament.patient_id == patient_id)\
        .filter(
            and_(
                models.PatientMedicament.start_date <= today,  # уже началось
                or_(
                    models.PatientMedicament.end_date.is_(None),  # нет даты окончания
                    models.PatientMedicament.end_date >= today  # еще не закончилось
                )
            )
        )\
        .all()
    
    patient_active_medicament_ids = set(pm.medicament_id for pm in patient_active_medicaments)
    
    # Получаем прямые противопоказания пациента к лекарствам
    patient_medicament_contraindications = db.query(models.PatientMedicamentContraindication)\
        .filter(models.PatientMedicamentContraindication.patient_id == patient_id)\
        .all()
    
    patient_contraindicated_medicament_ids = set(
        pmc.medicament_id for pmc in patient_medicament_contraindications
    )
    
    # Собираем ID всех лекарств, с которыми будут проверяться взаимодействия
    all_medicament_ids_to_check = set()
    medicaments_info = {}
    
    # Проверяем существование всех новых лекарств
    for medicament_data in medicaments_data.medicaments:
        medicament_id = medicament_data.medicament_id
        
        # Проверяем существование медикамента
        medicament = db.query(models.Medicament)\
            .filter(models.Medicament.id == medicament_id)\
            .first()
        
        if not medicament:
            raise HTTPException(
                status_code=404,
                detail=f"Медикамент с ID {medicament_id} не найден в справочнике"
            )
        
        medicaments_info[medicament_id] = {
            "name": medicament.name,
            "data": medicament_data
        }
        all_medicament_ids_to_check.add(medicament_id)
    
    added_medicaments = []
    conflicted_medicaments = []
    
    # Для каждого нового лекарства проверяем противопоказания
    for medicament_id, info in medicaments_info.items():
        medicament_name = info["name"]
        medicament_data = info["data"]
        conflict_reasons = []
        
        #Прямое противопоказание пациента к этому лекарству
        if medicament_id in patient_contraindicated_medicament_ids:
            conflict_reasons.append(f"Прямое противопоказание: пациент не переносит '{medicament_name}'")
        
        #Пациент уже принимает это лекарство (активно)
        if medicament_id in patient_active_medicament_ids:
            # Находим активное назначение этого лекарства
            active_prescriptions = [
                pm for pm in patient_active_medicaments 
                if pm.medicament_id == medicament_id
            ]
            
            if active_prescriptions:
                prescription = active_prescriptions[0]
                # Уточняем статус
                if prescription.end_date and prescription.end_date < today:
                    status = "закончилось"
                elif prescription.start_date > today:
                    status = "еще не началось"
                else:
                    status = "активно"
                    
                conflict_reasons.append(
                    f"Пациент уже принимает это лекарство (назначено {prescription.start_date}, статус: {status})"
                )
        
        #Взаимодействие с активными лекарствами пациента
        if patient_active_medicament_ids:
            # Находим все взаимодействия между новым лекарством и активными лекарствами пациента
            interactions = db.query(models.MedicamentMedicamentContraindication)\
                .filter(
                    or_(
                        and_(
                            models.MedicamentMedicamentContraindication.medication_first_id == medicament_id,
                            models.MedicamentMedicamentContraindication.medication_second_id.in_(list(patient_active_medicament_ids))
                        ),
                        and_(
                            models.MedicamentMedicamentContraindication.medication_second_id == medicament_id,
                            models.MedicamentMedicamentContraindication.medication_first_id.in_(list(patient_active_medicament_ids))
                        )
                    )
                )\
                .all()
            
            for interaction in interactions:
                # Определяем, с каким активным лекарством пациента есть взаимодействие
                other_medicament_id = (
                    interaction.medication_first_id 
                    if interaction.medication_first_id != medicament_id 
                    else interaction.medication_second_id
                )
                
                # Получаем название другого лекарства
                other_medicament = db.query(models.Medicament)\
                    .filter(models.Medicament.id == other_medicament_id)\
                    .first()
                
                if other_medicament:
                    # Находим активное назначение
                    patient_med = next(
                        (pm for pm in patient_active_medicaments 
                            if pm.medicament_id == other_medicament_id), 
                        None
                    )
                    
                    if patient_med:
                        # Определяем статус активного лекарства
                        if patient_med.end_date and patient_med.end_date < today:
                            status = "закончилось"
                        elif patient_med.start_date > today:
                            status = "еще не началось"
                        else:
                            status = "активно"
                            
                        conflict_reasons.append(
                            f"Взаимодействие с активным лекарством '{other_medicament.name}' (статус: {status})"
                        )
        
        #Взаимодействие с другими новыми лекарствами в этом же назначении
        for other_new_id in all_medicament_ids_to_check:
            if other_new_id == medicament_id:
                continue
                
            # Проверяем, есть ли взаимодействие между этими двумя лекарствами
            # Упорядочиваем ID для проверки (в таблице medication_first_id < medication_second_id)
            id1, id2 = sorted([medicament_id, other_new_id])
            
            interaction_exists = db.query(models.MedicamentMedicamentContraindication)\
                .filter(
                    models.MedicamentMedicamentContraindication.medication_first_id == id1,
                    models.MedicamentMedicamentContraindication.medication_second_id == id2
                )\
                .first()
            
            if interaction_exists:
                other_medicament_name = medicaments_info[other_new_id]["name"]
                conflict_reasons.append(
                    f"Взаимодействие с другим новым лекарством в этом назначении: '{other_medicament_name}'"
                )
        
        # Если есть конфликты, добавляем в список конфликтных
        if conflict_reasons:
            conflicted_medicaments.append({
                "medicament_id": medicament_id,
                "medicament_name": medicament_name,
                "conflict_reasons": conflict_reasons
            })
            continue
        
        # Если проверки прошли успешно - создаем запись
        db_medicament = models.PatientMedicament(
            patient_id=patient_id,
            medicament_id=medicament_id,
            dosage=medicament_data.dosage,
            frequency=medicament_data.frequency,
            start_date=medicament_data.start_date,
            end_date=medicament_data.end_date,
            doctor_by_id=current_doctor.id,
            appointment_id=appointment_id,
            notes=medicament_data.notes
        )
        
        db.add(db_medicament)
        added_medicaments.append(db_medicament)
    
    # Если лекарство не было добавлено
    if not added_medicaments:
        error_message = "Ни одно лекарство не было добавлено из-за медицинских противопоказаний:\n"
        for conflict in conflicted_medicaments:
            error_message += f"- {conflict['medicament_name']}:\n"
            for reason in conflict['conflict_reasons']:
                error_message += f"  • {reason}\n"
        
        raise HTTPException(
            status_code=422,
            detail=error_message.strip()
        )

    # Добавляем подпись доктора к информации о назначении
    medicament_names = [medicaments_info[m.medicament_id]["name"] for m in added_medicaments]
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


    db.commit()

    # Обновляем объекты
    for medicament in added_medicaments:
        db.refresh(medicament)

    # Подготавливаем ответ
    added_medicaments_response = []
    for m in added_medicaments:
        # Получаем название лекарства
        medicament = db.query(models.Medicament)\
            .filter(models.Medicament.id == m.medicament_id)\
            .first()
        
        # Создаем объект для ответа
        medicament_dict = {
            "id": m.id,
            "patient_id": m.patient_id,
            "medicament_id": m.medicament_id,
            "medicament_name": medicament.name if medicament else "Неизвестно",
            "dosage": m.dosage,
            "frequency": m.frequency,
            "start_date": m.start_date,
            "end_date": m.end_date,
            "notes": m.notes,
            "doctor_id": current_doctor.id,
            "appointment_id": appointment_id
        }
        added_medicaments_response.append(medicament_dict)

    # Создаем ответ
    response_data = {
        "added_medicaments": added_medicaments_response,
        "conflicts": [
            {
                "medicament_id": conflict.get("medicament_id"),
                "medicament_name": conflict["medicament_name"],
                "conflict_reasons": conflict["conflict_reasons"]
            }
            for conflict in conflicted_medicaments
        ],
        "warning": warning_message,
        "message": success_message
    }
    
    response = schemas.MedicamentsAppointmentResponse(**response_data)
    
    return response
        
@router.post("/appointments/{appointment_id}/medicaments", response_model=schemas.MedicamentsAppointmentResponse)
@exceptions.handle_exceptions(custom_message="Не удалось добавить лекарство")
def add_medicaments_for_appointment(
    appointment_id: int,
    medicaments_data: schemas.MedicamentsForAppointmentRequest,
    current_doctor: models.Doctor = Depends(oauth2.get_current_doctor),
    db: Session = Depends(get_db)
):
    """
    Добавление лекарств пациенту с проверкой медицинских противопоказаний.
    Проверяются только:
    1. Прямые противопоказания пациента к лекарствам (PatientMedicamentContraindication)
    2. Взаимодействия между лекарствами (MedicamentMedicamentContraindication)
    """
    from datetime import date

    # Получаем запись на прием
    db_appointment = db.query(models.Appointment)\
        .filter(models.Appointment.id == appointment_id)\
        .first()
    
    if not db_appointment: 
        raise HTTPException(
            status_code=404,
            detail=f"Запись на прием с ID {appointment_id} не найдена"
        )
    
    # Проверяем, что запись относится к текущему доктору
    schedule = db.query(models.Schedule)\
        .filter(models.Schedule.id == db_appointment.schedule_id)\
        .first()
    
    if not schedule or schedule.doctor_id != current_doctor.id:
        raise HTTPException(
            status_code=403,
            detail="Эта запись не относится к вашему расписанию"
        )
    
    patient_id = db_appointment.patient_id
    today = date.today()
    
    #Получаем только act. лекарства пациента
    
    patient_active_medicaments = db.query(models.PatientMedicament)\
        .filter(models.PatientMedicament.patient_id == patient_id)\
        .filter(
            and_(
                models.PatientMedicament.start_date <= today,  # уже началось
                or_(
                    models.PatientMedicament.end_date.is_(None),  # нет даты окончания
                    models.PatientMedicament.end_date >= today  # еще не закончилось
                )
            )
        )\
        .all()
    
    patient_active_medicament_ids = set(pm.medicament_id for pm in patient_active_medicaments)
    
    # Получаем прямые противопоказания пациента к лекарствам
    patient_medicament_contraindications = db.query(models.PatientMedicamentContraindication)\
        .filter(models.PatientMedicamentContraindication.patient_id == patient_id)\
        .all()
    
    patient_contraindicated_medicament_ids = set(
        pmc.medicament_id for pmc in patient_medicament_contraindications
    )
    
    # Собираем ID всех лекарств, с которыми будут проверяться взаимодействия
    all_medicament_ids_to_check = set()
    medicaments_info = {}
    
    # Проверяем существование всех новых лекарств
    for medicament_data in medicaments_data.medicaments:
        medicament_id = medicament_data.medicament_id
        
        # Проверяем существование медикамента
        medicament = db.query(models.Medicament)\
            .filter(models.Medicament.id == medicament_id)\
            .first()
        
        if not medicament:
            raise HTTPException(
                status_code=404,
                detail=f"Медикамент с ID {medicament_id} не найден в справочнике"
            )
        
        medicaments_info[medicament_id] = {
            "name": medicament.name,
            "data": medicament_data
        }
        all_medicament_ids_to_check.add(medicament_id)
    
    added_medicaments = []
    conflicted_medicaments = []
    
    # Для каждого нового лекарства проверяем противопоказания
    for medicament_id, info in medicaments_info.items():
        medicament_name = info["name"]
        medicament_data = info["data"]
        conflict_reasons = []
        
        #Прямое противопоказание пациента к этому лекарству
        if medicament_id in patient_contraindicated_medicament_ids:
            conflict_reasons.append(f"Прямое противопоказание: пациент не переносит '{medicament_name}'")
        
        #Пациент уже принимает это лекарство (активно)
        if medicament_id in patient_active_medicament_ids:
            # Находим активное назначение этого лекарства
            active_prescriptions = [
                pm for pm in patient_active_medicaments 
                if pm.medicament_id == medicament_id
            ]
            
            if active_prescriptions:
                prescription = active_prescriptions[0]
                # Уточняем статус
                if prescription.end_date and prescription.end_date < today:
                    status = "закончилось"
                elif prescription.start_date > today:
                    status = "еще не началось"
                else:
                    status = "активно"
                    
                conflict_reasons.append(
                    f"Пациент уже принимает это лекарство (назначено {prescription.start_date}, статус: {status})"
                )
        
        #Взаимодействие с активными лекарствами пациента
        if patient_active_medicament_ids:
            # Находим все взаимодействия между новым лекарством и активными лекарствами пациента
            interactions = db.query(models.MedicamentMedicamentContraindication)\
                .filter(
                    or_(
                        and_(
                            models.MedicamentMedicamentContraindication.medication_first_id == medicament_id,
                            models.MedicamentMedicamentContraindication.medication_second_id.in_(list(patient_active_medicament_ids))
                        ),
                        and_(
                            models.MedicamentMedicamentContraindication.medication_second_id == medicament_id,
                            models.MedicamentMedicamentContraindication.medication_first_id.in_(list(patient_active_medicament_ids))
                        )
                    )
                )\
                .all()
            
            for interaction in interactions:
                # Определяем, с каким активным лекарством пациента есть взаимодействие
                other_medicament_id = (
                    interaction.medication_first_id 
                    if interaction.medication_first_id != medicament_id 
                    else interaction.medication_second_id
                )
                
                # Получаем название другого лекарства
                other_medicament = db.query(models.Medicament)\
                    .filter(models.Medicament.id == other_medicament_id)\
                    .first()
                
                if other_medicament:
                    # Находим активное назначение
                    patient_med = next(
                        (pm for pm in patient_active_medicaments 
                            if pm.medicament_id == other_medicament_id), 
                        None
                    )
                    
                    if patient_med:
                        # Определяем статус активного лекарства
                        if patient_med.end_date and patient_med.end_date < today:
                            status = "закончилось"
                        elif patient_med.start_date > today:
                            status = "еще не началось"
                        else:
                            status = "активно"
                            
                        conflict_reasons.append(
                            f"Взаимодействие с активным лекарством '{other_medicament.name}' (статус: {status})"
                        )
        
        #Взаимодействие с другими новыми лекарствами в этом же назначении
        for other_new_id in all_medicament_ids_to_check:
            if other_new_id == medicament_id:
                continue
                
            # Проверяем, есть ли взаимодействие между этими двумя лекарствами
            # Упорядочиваем ID для проверки (в таблице medication_first_id < medication_second_id)
            id1, id2 = sorted([medicament_id, other_new_id])
            
            interaction_exists = db.query(models.MedicamentMedicamentContraindication)\
                .filter(
                    models.MedicamentMedicamentContraindication.medication_first_id == id1,
                    models.MedicamentMedicamentContraindication.medication_second_id == id2
                )\
                .first()
            
            if interaction_exists:
                other_medicament_name = medicaments_info[other_new_id]["name"]
                conflict_reasons.append(
                    f"Взаимодействие с другим новым лекарством в этом назначении: '{other_medicament_name}'"
                )
        
        # Если есть конфликты, добавляем в список конфликтных
        if conflict_reasons:
            conflicted_medicaments.append({
                "medicament_id": medicament_id,
                "medicament_name": medicament_name,
                "conflict_reasons": conflict_reasons
            })
            continue
        
        # Если проверки прошли успешно - создаем запись
        db_medicament = models.PatientMedicament(
            patient_id=patient_id,
            medicament_id=medicament_id,
            dosage=medicament_data.dosage,
            frequency=medicament_data.frequency,
            start_date=medicament_data.start_date,
            end_date=medicament_data.end_date,
            doctor_by_id=current_doctor.id,
            appointment_id=appointment_id,
            notes=medicament_data.notes
        )
        
        db.add(db_medicament)
        added_medicaments.append(db_medicament)
    
    # Если лекарство не было добавлено
    if not added_medicaments:
        error_message = "Ни одно лекарство не было добавлено из-за медицинских противопоказаний:\n"
        for conflict in conflicted_medicaments:
            error_message += f"- {conflict['medicament_name']}:\n"
            for reason in conflict['conflict_reasons']:
                error_message += f"  • {reason}\n"
        
        raise HTTPException(
            status_code=422,
            detail=error_message.strip()
        )

    # Добавляем подпись доктора к информации о назначении
    medicament_names = [medicaments_info[m.medicament_id]["name"] for m in added_medicaments]
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


    db.commit()

    # Обновляем объекты
    for medicament in added_medicaments:
        db.refresh(medicament)

    # Подготавливаем ответ
    added_medicaments_response = []
    for m in added_medicaments:
        # Получаем название лекарства
        medicament = db.query(models.Medicament)\
            .filter(models.Medicament.id == m.medicament_id)\
            .first()
        
        # Создаем объект для ответа
        medicament_dict = {
            "id": m.id,
            "patient_id": m.patient_id,
            "medicament_id": m.medicament_id,
            "medicament_name": medicament.name if medicament else "Неизвестно",
            "dosage": m.dosage,
            "frequency": m.frequency,
            "start_date": m.start_date,
            "end_date": m.end_date,
            "notes": m.notes,
            "doctor_id": current_doctor.id,
            "appointment_id": appointment_id
        }
        added_medicaments_response.append(medicament_dict)

    # Создаем ответ
    response_data = {
        "added_medicaments": added_medicaments_response,
        "conflicts": [
            {
                "medicament_id": conflict.get("medicament_id"),
                "medicament_name": conflict["medicament_name"],
                "conflict_reasons": conflict["conflict_reasons"]
            }
            for conflict in conflicted_medicaments
        ],
        "warning": warning_message,
        "message": success_message
    }
    
    response = schemas.MedicamentsAppointmentResponse(**response_data)
    
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
    medicament_data: schemas.MedicamentCreate,
    current_doctor: models.Doctor = Depends(oauth2.get_current_doctor),
    db: Session = Depends(get_db)
):
    """
    Добавить новый медикамент в справочник со связями с другими медикаментами.
    Создает медикамент и сразу добавляет связи с противопоказанными медикаментами.
    Изменения выполняются в одной транзакции - либо все успешно, либо все откатывается.
    """
        # Проверяем, нет ли уже такого медикамента по названию
    existing = db.query(models.Medicament)\
        .filter(models.Medicament.name == medicament_data.medicament_name.capitalize())\
        .first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Медикамент с таким названием уже существует"
        )
    
    #Создаем новый медикамент
    new_medicament = models.Medicament(
        name=medicament_data.medicament_name.capitalize()
    )
    
    db.add(new_medicament)
    db.flush()  # Получаем ID нового медикамента, но пока что не коммитим
    
    #Проверяем существование всех указанных противопоказанных медикаментов
    if medicament_data.med_contraindications_ids:
        existing_medicaments = db.query(models.Medicament)\
            .filter(models.Medicament.id.in_(medicament_data.med_contraindications_ids))\
            .all()
        
        existing_ids = {med.id for med in existing_medicaments}
        requested_ids = set(medicament_data.med_contraindications_ids)
        
        # Проверяем, все ли существуют
        missing_ids = requested_ids - existing_ids
        if missing_ids:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Медикаменты с ID {missing_ids} не найдены"
            )
        
        #Создаем связи между медикаментами
        created_links = []
        for other_medicament_id in medicament_data.med_contraindications_ids:
            if other_medicament_id == new_medicament.id:
                continue
            
            # Упорядочиваем id
            id1, id2 = sorted([new_medicament.id, other_medicament_id])
            
            # Создаем новую связь
            new_link = models.MedicamentMedicamentContraindication(
                medication_first_id=id1,
                medication_second_id=id2
            )
            
            db.add(new_link)
            created_links.append(other_medicament_id)
    
    db.commit()
    

    result = {
        "id": new_medicament.id,
        "name": new_medicament.name,
        "message": "Медикамент успешно добавлен"
    }
    
    if medicament_data.med_contraindications_ids:
        # Получаем названия связанных медикаментов для ответа
        linked_medicaments = db.query(models.Medicament)\
            .filter(models.Medicament.id.in_(created_links))\
            .all()
        
        result["created_links"] = [
            {
                "medicament_id": med.id,
                "medicament_name": med.name
            }
            for med in linked_medicaments
        ]
        result["message"] = f"Медикамент успешно добавлен с {len(created_links)} противопоказаниями"
    
    return result
    



@router.delete("/medicaments/{medicament_id}", response_model=dict)
@exceptions.handle_exceptions(custom_message="Не удалось удалить медикамент")
def delete_medicament(
    medicament_id: int,
    current_doctor: models.Doctor = Depends(oauth2.get_current_doctor),
    db: Session = Depends(get_db)
):
    """
    Удалить медикамент из справочника.
    Удаление возможно только если нет активных назначений этого медикамента пациентам.
    Автоматически удаляет все связанные противопоказания и взаимодействия.
    """
    medicament = db.query(models.Medicament)\
        .filter(models.Medicament.id == medicament_id)\
        .first()
    
    if not medicament:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Медикамент не найден"
        )
    
    # есть ли активные назначения этого медикамента пациентам
    active_prescriptions = db.query(models.PatientMedicament)\
        .filter(
            models.PatientMedicament.medicament_id == medicament_id,
            models.PatientMedicament.end_date.is_(None)  # назначения без даты окончания
        )\
        .all()
    
    #проверяем назначения с датой окончания в будущем
    future_prescriptions = db.query(models.PatientMedicament)\
        .filter(
            models.PatientMedicament.medicament_id == medicament_id,
            models.PatientMedicament.end_date >= date.today()
        )\
        .all()
    
    all_active_prescriptions = list(set(active_prescriptions + future_prescriptions))
    
    if all_active_prescriptions:
        patient_ids = list(set([pm.patient_id for pm in all_active_prescriptions]))
        patients = db.query(models.Patient)\
            .filter(models.Patient.id.in_(patient_ids))\
            .all()
        
        patient_names = [
            f"{p.last_name} {p.first_name} {p.patronymic}" 
            for p in patients
        ]
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"Невозможно удалить медикамент '{medicament.name}', так как он назначен пациентам",
                "medicament_id": medicament_id,
                "medicament_name": medicament.name,
                "affected_patients": patient_names,
                "active_prescriptions_count": len(all_active_prescriptions),
                "suggestion": "Сначала отмените все активные назначения этого медикамента"
            }
        )
    
    #Проверяем, есть ли неактивные
    historical_prescriptions = db.query(models.PatientMedicament)\
        .filter(
            models.PatientMedicament.medicament_id == medicament_id,
            models.PatientMedicament.end_date < date.today()
        )\
        .count()
    

    # Взаимодействия с другими медикаментами
    interactions_as_first = db.query(models.MedicamentMedicamentContraindication)\
        .filter(models.MedicamentMedicamentContraindication.medication_first_id == medicament_id)\
        .count()
    
    interactions_as_second = db.query(models.MedicamentMedicamentContraindication)\
        .filter(models.MedicamentMedicamentContraindication.medication_second_id == medicament_id)\
        .count()
    
    total_interactions = interactions_as_first + interactions_as_second
    
    # Прямые противопоказания пациентов
    patient_contraindications = db.query(models.PatientMedicamentContraindication)\
        .filter(models.PatientMedicamentContraindication.medicament_id == medicament_id)\
        .count()
    
    # Связи с другими противопоказаниями
    other_contraindications = db.query(models.MedicationContraindicationOther)\
        .filter(models.MedicationContraindicationOther.medicament_id == medicament_id)\
        .count()

    
    # Удаляем неактивные назначения пациентам
    if historical_prescriptions > 0:
        db.query(models.PatientMedicament)\
            .filter(
                models.PatientMedicament.medicament_id == medicament_id,
                models.PatientMedicament.end_date < date.today()
            )\
            .delete(synchronize_session=False)
    
    # Удаляем прямые противопоказания пациентов к этому медикаменту
    if patient_contraindications > 0:
        db.query(models.PatientMedicamentContraindication)\
            .filter(models.PatientMedicamentContraindication.medicament_id == medicament_id)\
            .delete(synchronize_session=False)
    
    #Удаляем связи с другими противопоказаниями
    if other_contraindications > 0:
        db.query(models.MedicationContraindicationOther)\
            .filter(models.MedicationContraindicationOther.medicament_id == medicament_id)\
            .delete(synchronize_session=False)
    
    #Удаляем взаимодействия с другими медикаментами
    if total_interactions > 0:
        # Удаляем где медикамент первый
        db.query(models.MedicamentMedicamentContraindication)\
            .filter(models.MedicamentMedicamentContraindication.medication_first_id == medicament_id)\
            .delete(synchronize_session=False)
        
        # Удаляем где медикамент второй
        db.query(models.MedicamentMedicamentContraindication)\
            .filter(models.MedicamentMedicamentContraindication.medication_second_id == medicament_id)\
            .delete(synchronize_session=False)
    
    # Удаляем сам медикамент
    db.delete(medicament)
    
    db.commit()
    
    report = {
        "message": f"Медикамент '{medicament.name}' успешно удален",
        "deleted_id": medicament_id,
        "deleted_name": medicament.name,
        "deleted_statistics": {
            "historical_prescriptions_deleted": historical_prescriptions,
            "patient_contraindications_deleted": patient_contraindications,
            "other_contraindications_deleted": other_contraindications,
            "medicament_interactions_deleted": total_interactions,
        },
        "note": "Все связанные записи были удалены автоматически"
    }
    
    return report
        
   


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
    contraindication_data: schemas.CreateWithName,
    current_doctor: models.Doctor = Depends(oauth2.get_current_doctor),
    db: Session = Depends(get_db)
):
    """
    Добавить новое противопоказание в справочник
    """
    existing = db.query(models.OtherContraindication)\
        .filter(models.OtherContraindication.name == contraindication_data.name)\
        .first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Противопоказание с таким названием уже существует"
        )
    
    new_contraindication = models.OtherContraindication(
        name=contraindication_data.name.capitalize()
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
    interaction_data: schemas.MedMedContr,  # {"first_medicament_id": 1, "second_medicament_id": 2}
    current_doctor: models.Doctor = Depends(oauth2.get_current_doctor),
    db: Session = Depends(get_db)
):
    """
    Добавить противопоказанное взаимодействие между медикаментами
    """
    # Упорядочиваем ID (меньший первый)
    id1, id2 = sorted([interaction_data.first_medicament_id, 
                       interaction_data.second_medicament_id])
    
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
    link_data: schemas.MedicamentContr,
    current_doctor: models.Doctor = Depends(oauth2.get_current_doctor),
    db: Session = Depends(get_db)
):
    """
    Добавить связь между медикаментом и противопоказанием
    """
    medicament_id = link_data.medicament_id
    contraindication_id = link_data.contraindication_id
    
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
            "medicament_name": medicament.name,
            "contraindication_id": contraindication.id,
            "contraindication_name": contraindication.name
        }
        for link, medicament, contraindication in results
    ]


@router.delete("/interactions", response_model=dict)
@exceptions.handle_exceptions(custom_message="Не удалось удалить взаимодействие медикаментов")
def remove_medicament_interaction(
    interaction_data: schemas.MedMedContr, # {"medicament1_id": 1, "medicament2_id": 2}
    current_doctor: models.Doctor = Depends(oauth2.get_current_doctor),
    db: Session = Depends(get_db)
):
    """
    Удалить взаимодействие между двумя медикаментами
    Принимает JSON: {"medicament1_id": 1, "medicament2_id": 2}
    """
    medicament1_id = interaction_data.first_medicament_id
    medicament2_id = interaction_data.second_medicament_id
    
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
    link_data: schemas.MedicamentContr,  # {"medicament_id": 1, "contraindication_id": 2}
    current_doctor: models.Doctor = Depends(oauth2.get_current_doctor),
    db: Session = Depends(get_db)
):
    """
    Удалить связь между медикаментом и противопоказанием
    Принимает JSON: {"medicament_id": 1, "contraindication_id": 2}
    """
    medicament_id = link_data.medicament_id
    contraindication_id = link_data.contraindication_id
    
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
    
    #Получаем взаимодействия с другими медикаментами
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
    
    #Получаем другие противопоказания медикамента
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
    data: schemas.PatientMedContr,  # {"patient_id": 1, "medicament_id": 2}
    current_doctor: models.Doctor = Depends(oauth2.get_current_doctor),
    db: Session = Depends(get_db)
):
    """
    Добавить противопоказание пациента к медикаменту
    Принимает JSON: {"patient_id": 1, "contraindication_medicament_id": 2}
    """
    patient_id = data.patient_id
    medicament_id = data.contraindication_medicament_id
    
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
    data: schemas.PatientMedContr,  # {"patient_id": 1, "medicament_id": 2}
    current_doctor: models.Doctor = Depends(oauth2.get_current_doctor),
    db: Session = Depends(get_db)
):
    """
    Удалить противопоказание пациента к медикаменту
    Принимает JSON: {"patient_id": 1, "medicament_id": 2}
    """
    patient_id = data.patient_id
    medicament_id = data.contraindication_medicament_id
    
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
    data: schemas.PatientContr,  # {"patient_id": 1, "contraindication_id": 2}
    current_doctor: models.Doctor = Depends(oauth2.get_current_doctor),
    db: Session = Depends(get_db)
):
    """
    Добавить общее противопоказание пациента
    Принимает JSON: {"patient_id": 1, "contraindication_id": 2}
    """
    patient_id = data.patient_id
    contraindication_id = data.contraindication_id
    
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
    data: schemas.PatientContr,  # {"patient_id": 1, "contraindication_id": 2}
    current_doctor: models.Doctor = Depends(oauth2.get_current_doctor),
    db: Session = Depends(get_db)
):
    """
    Удалить общее противопоказание пациента
    Принимает JSON: {"patient_id": 1, "contraindication_id": 2}
    """
    patient_id = data.patient_id
    contraindication_id = data.contraindication_id
    
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
        "message": f"Удалено противопоказание: пациент '{patient.first_name}' не имеет противопоказания к '{contraindication.name}'",
        "patient_id": patient_id,
        "contraindication_id": contraindication_id
    }

@router.get("/patient/{patient_id}/medication", response_model=dict)
@exceptions.handle_exceptions(custom_message="Не удалось получить отчёт о лекарствах пациента")
def get_patient_medication_report(
    patient_id:int,
    current_doctor: models.Doctor = Depends(oauth2.get_current_doctor),
    db: Session = Depends(get_db)
):
    """
    Отчет о лекарствах пациента и противопоказаниях.
    """

    current_patient=patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
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
        "other contraindications": [
            {
                "contraindication_id": poc.contraindication_id,
                "contraindication_name": poc.contraindication.name,
                "type": "Общее противопоказание"
            }
            for poc in patient_other_contraindications
        ]
    }
    
    return report


@router.delete("/patient-medicaments/{patient_medicament_id}")
@exceptions.handle_exceptions(custom_message="Не удалось удалить назначенное лекарство")
def delete_patient_medicament(
    patient_medicament_id: int,
    current_doctor: models.Doctor = Depends(oauth2.get_current_doctor),
    db: Session = Depends(get_db)
):
    """
    Удаление назначенного лекарства пациента.
    Доктор может удалять только лекарства, которые он сам назначил.
    """
    
    # Находим назначенное лекарство
    patient_medicament = db.query(models.PatientMedicament)\
        .filter(models.PatientMedicament.id == patient_medicament_id)\
        .first()
    
    if not patient_medicament:
        raise HTTPException(
            status_code=404,
            detail=f"Назначенное лекарство с ID {patient_medicament_id} не найдено"
        )
    
    # Проверяем, что доктор является тем, кто назначил это лекарство
    if patient_medicament.doctor_by_id != current_doctor.id:
        raise HTTPException(
            status_code=403,
            detail="Вы можете удалять только лекарства, которые назначили сами"
        )
    
    # Проверяем, есть ли связанная запись приема
    appointment_info = ""
    if patient_medicament.appointment_id:
        appointment_info = f" (назначено на приеме ID: {patient_medicament.appointment_id})"
    
    # Удаляем
    db.delete(patient_medicament)
    db.commit()
    
    return {
        "message": f"Назначенное лекарство успешно удалено{appointment_info}",
        "deleted_id": patient_medicament_id,
        "medicament_id": patient_medicament.medicament_id,
        "patient_id": patient_medicament.patient_id
    }


@router.get("/my-prescriptions", response_model=List[schemas.PatientMedicamentResponse])
@exceptions.handle_exceptions(custom_message="Не удалось получить список назначений")
def get_my_prescriptions(
    current_doctor: models.Doctor = Depends(oauth2.get_current_doctor),
    db: Session = Depends(get_db)
):
    """
    Получение всех назначений лекарств, сделанных текущим доктором.
    """
    
    prescriptions = db.query(models.PatientMedicament)\
        .filter(models.PatientMedicament.doctor_by_id == current_doctor.id)\
        .order_by(models.PatientMedicament.start_date.desc())\
        .all()
    
    # Формируем ответ
    result = []
    for prescription in prescriptions:
        # Получаем название лекарства
        medicament = db.query(models.Medicament)\
            .filter(models.Medicament.id == prescription.medicament_id)\
            .first()
        
        # Получаем данные пациента
        patient = db.query(models.Patient)\
            .filter(models.Patient.id == prescription.patient_id)\
            .first()
        
        # Создаем объект для ответа
        prescription_data = {
            "id": prescription.id,
            "patient_id": prescription.patient_id,
            "patient_name": f"{patient.first_name} {patient.last_name}" if patient else "Неизвестный пациент",
            "medicament_id": prescription.medicament_id,
            "medicament_name": medicament.name if medicament else "Неизвестное лекарство",
            "dosage": prescription.dosage,
            "frequency": prescription.frequency,
            "start_date": prescription.start_date,
            "end_date": prescription.end_date,
            "notes": prescription.notes,
            "doctor_id": prescription.doctor_by_id,
            "appointment_id": prescription.appointment_id,
            "created_at": prescription.created_at
        }
        
        result.append(prescription_data)
    
    return result
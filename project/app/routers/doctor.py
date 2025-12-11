import models,schemas,oauth2,utils
from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from database import get_db
from typing import Optional,List
from sqlalchemy import func, and_
from sqlalchemy.exc import IntegrityError
from datetime import timedelta
from datetime import date

router = APIRouter(
    prefix = "/doctor",
    tags=['doctor']
)

@router.post("/medicaments/contraindications", response_model=dict)
def add_medicament_contradiction(
    request_data: schemas.MedicamentContradictionsRequest,
    current_doctor: models.Doctor = Depends(oauth2.get_current_doctor),  # ← Добавлено
    db: Session = Depends(get_db)
):
    """
    Добавление противопоказаний для лекарства.
    """
    try:
        medicament_name = request_data.medicament_name
        contradictions = request_data.contradictions
        added_count = 0
        
        for contradiction in contradictions:
            existing = db.query(models.Contradiction)\
                .filter(
                    and_(
                        models.Contradiction.medicament_name == medicament_name,
                        models.Contradiction.contradiction == contradiction
                    )
                )\
                .first()
            
            if existing:
                continue
            
            db_contradiction = models.Contradiction(
                medicament_name=medicament_name,
                contradiction=contradiction
            )
            
            db.add(db_contradiction)
            added_count += 1
        
        if added_count > 0:
            db.commit()
            return {
                "status": "success",
                "message": f"Добавлено {added_count} противопоказаний для лекарства '{medicament_name}'",
                "medicament_name": medicament_name,
                "added_contradictions": contradictions,
                "added_by_doctor": f"Dr. {current_doctor.last_name}"
            }
        else:
            return {
                "status": "info",
                "message": "Все указанные противопоказания уже существуют",
                "medicament_name": medicament_name
            }
            
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ошибка целостности данных: {str(e)}"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при добавлении противопоказаний: {str(e)}"
        )
    

@router.get("/medicaments/contraindications", response_model=List[dict])
def get_medicament_contradictions(
    medicament_name: Optional[str] = None,
    current_doctor: models.Doctor = Depends(oauth2.get_current_doctor),  # ← Добавлено
    db: Session = Depends(get_db)
):
    """
    Получение списка противопоказаний для лекарств.
    """
    try:
        query = db.query(models.Contradiction)
        
        if medicament_name:
            query = query.filter(models.Contradiction.medicament_name == medicament_name)
        
        contradictions = query.all()
        
        result = []
        for c in contradictions:
            result.append({
                "medicament_name": c.medicament_name,
                "contradiction": c.contradiction
            })
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении противопоказаний: {str(e)}"
        )


@router.delete("/medicaments/contraindications", response_model=dict)
def delete_medicament_contradiction(
    request_data: schemas.MedicamentContradictionRequest,
    current_doctor: models.Doctor = Depends(oauth2.get_current_doctor),  # ← Добавлено
    db: Session = Depends(get_db)
):
    """
    Удаление конкретного противопоказания для лекарства.
    """
    try:
        medicament_name = request_data.medicament_name
        contradiction = request_data.contradictions
        
        db_contradiction = db.query(models.Contradiction)\
            .filter(
                and_(
                    models.Contradiction.medicament_name == medicament_name,
                    models.Contradiction.contradiction == contradiction
                )
            )\
            .first()
        
        if not db_contradiction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Противопоказание '{contradiction}' для лекарства '{medicament_name}' не найдено"
            )
        
        db.delete(db_contradiction)
        db.commit()
        
        return {
            "status": "success",
            "message": f"Противопоказание '{contradiction}' удалено для лекарства '{medicament_name}'",
            "deleted_by_doctor": f"Dr. {current_doctor.last_name}"
        }
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при удалении противопоказания: {str(e)}"
        )
    

@router.put("/appointments/{appointment_id}", response_model=schemas.AppointmentResponse)
def update_appointment_info(
    appointment_id: int,
    update_data: schemas.AppointmentUpdate,
    current_doctor: models.Doctor = Depends(oauth2.get_current_doctor),  # ← Добавлено
    db: Session = Depends(get_db)
):
    """
    Обновление информации о записи на прием.
    """
    try:
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
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при обновлении записи на прием: {str(e)}"
        )
    
@router.post("/appointments/{appointment_id}/medicaments", response_model=schemas.MedicamentsAppointmentResponse)
def add_medicaments_for_appointment(
    appointment_id: int,
    medicaments_data: schemas.MedicamentsForAppointmentRequest,
    current_doctor: models.Doctor = Depends(oauth2.get_current_doctor),  # ← Добавлено
    db: Session = Depends(get_db)
):
    """
    Добавление лекарств пациенту на основе appointment ID.
    """
    try:
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
                            models.Contradiction.medicament_name.in_([pm.medicament_name for pm in patient_medicaments]),
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
                medicament_name=medicament_data.medicament_name,
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
        medicament_names = [m.medicament_name for m in added_medicaments]
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
        
    except HTTPException:
        db.rollback()
        raise
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ошибка целостности данных: {str(e)}"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при добавлении лекарств: {str(e)}"
        )
    
# Получение всех записей на прием к текущему доктору
@router.get("/appointments", response_model=List[schemas.AppointmentResponse])
def get_my_appointments(
    current_doctor: models.Doctor = Depends(oauth2.get_current_doctor),
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Получение всех записей на прием к текущему доктору
    """
    try:
        # Получаем ID расписаний доктора
        doctor_schedule_ids = db.query(models.Schedule.id)\
            .filter(models.Schedule.doctor_id == current_doctor.id)\
            .subquery()
        
        # Запрос на записи к доктору
        query = db.query(models.Appointment)\
            .filter(models.Appointment.schedule_id.in_(doctor_schedule_ids))
        
        if status_filter:
            query = query.filter(models.Appointment.status == status_filter)
        
        appointments = query.order_by(models.Appointment.id.desc()).all()
        
        return appointments
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении записей: {str(e)}"
        )



@router.get("/patients/{patient_id}/medicaments", response_model=List[schemas.PatientMedicamentResponse])
def get_patient_medicaments(
    patient_id: int,
    current_doctor: models.Doctor = Depends(oauth2.get_current_doctor),
    db: Session = Depends(get_db)
):
    """
    Получение всех лекарств пациента.
    Доктор может просматривать лекарства любого пациента.
    """
    try:
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
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении лекарств пациента: {str(e)}"
        )
    
@router.get("/patients/{patient_id}/medicaments/active", response_model=List[schemas.PatientMedicamentResponse])
def get_patient_active_medicaments(
    patient_id: int,
    current_doctor: models.Doctor = Depends(oauth2.get_current_doctor),
    db: Session = Depends(get_db)
):
    """
    Получение только активных лекарств пациента (без end_date или с end_date в будущем).
    """
    try:
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
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении активных лекарств: {str(e)}"
        )
    
@router.get("/patients/{patient_id}/medication", response_model=dict)
def get_patient_medication_report(
    patient_id: int,
    current_doctor: models.Doctor = Depends(oauth2.get_current_doctor),
    db: Session = Depends(get_db)
):
    """
    Полный отчет о лекарствах и противопоказаниях пациента.
    Возвращает лекарства пациента + все противопоказания (прямые и из базы лекарств).
    """
    try:
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
    

@router.post("/patients/{patient_id}/contraindications", response_model=dict)
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
    try:
        # Проверяем существование пациента
        patient = db.query(models.Patient)\
            .filter(models.Patient.id == patient_id)\
            .first()
        
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Пациент с ID {patient_id} не найден"
            )
        
        contradictions = request_data.contradictions
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
            
    except IntegrityError as e:
        db.rollback()
        if "check_contradiction_name_length" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Название противопоказания должно быть от 1 до 100 символов"
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ошибка целостности данных: {str(e)}"
        )
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при добавлении противопоказаний: {str(e)}"
        )
    
@router.delete("/patients/{patient_id}/contraindications", response_model=dict)
def delete_patient_contradiction(
    patient_id: int,
    request_data: schemas.PatientContraindicationDeleteRequest,
    current_doctor: models.Doctor = Depends(oauth2.get_current_doctor),
    db: Session = Depends(get_db)
):
    """
    Удаление конкретного противопоказания пациента.
    """
    try:
        # Проверяем существование пациента
        patient = db.query(models.Patient)\
            .filter(models.Patient.id == patient_id)\
            .first()
        
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Пациент с ID {patient_id} не найден"
            )
        
        contradiction = request_data.contradiction
        
        # Находим противопоказание
        db_contradiction = db.query(models.PatientContradiction)\
            .filter(
                and_(
                    models.PatientContradiction.patient_id == patient_id,
                    models.PatientContradiction.contradiction == contradiction
                )
            )\
            .first()
        
        if not db_contradiction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Противопоказание '{contradiction}' у пациента не найдено"
            )
        
        # Удаляем противопоказание
        db.delete(db_contradiction)
        db.commit()
        
        return {
            "status": "success",
            "message": f"Противопоказание '{contradiction}' удалено у пациента",
            "patient_id": patient_id,
            "patient_name": f"{patient.last_name} {patient.first_name}",
            "deleted_by_doctor": f"Dr. {current_doctor.last_name}"
        }
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при удалении противопоказания: {str(e)}"
        )

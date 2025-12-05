import models,schemas
from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from database import get_db
from typing import Optional,List
from sqlalchemy import func, and_
from sqlalchemy.exc import IntegrityError
from datetime import timedelta

router = APIRouter(
    prefix = "/doctor",
    tags=['doctor']
)

@router.post("/medicaments/contraindications", response_model=dict)
def add_medicament_contradiction(
    request_data: schemas.MedicamentContradictionsRequest,  # Принимаем данные из тела запроса
    db: Session = Depends(get_db)
):
    """
    Добавление противопоказаний для лекарства.
    
    Args:
        medicament_name: Название лекарства
        contradictions: Список противопоказаний
    """
    try:
        medicament_name = request_data.medicament_name
        contradictions = request_data.contradictions
        added_count = 0
        
        for contradiction in contradictions:
            # Проверяем, не существует ли уже такая запись
            existing = db.query(models.Contradiction)\
                .filter(
                    and_(
                        models.Contradiction.medicament_name == medicament_name,
                        models.Contradiction.contradiction == contradiction
                    )
                )\
                .first()
            
            if existing:
                continue  # Пропускаем, если уже существует
            
            # Создаем новую запись о противопоказании
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
                "added_contradictions": contradictions
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
    db: Session = Depends(get_db)
):
    """
    Получение списка противопоказаний для лекарств.
    
    Args:
        medicament_name: Фильтр по названию лекарства (опционально)
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
    db: Session = Depends(get_db)
):
    """
    Удаление конкретного противопоказания для лекарства.
    """
    try:
        medicament_name = request_data.medicament_name
        contradiction = request_data.contradictions
        # Находим запись
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
            "message": f"Противопоказание '{contradiction}' удалено для лекарства '{medicament_name}'"
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
    db: Session = Depends(get_db)
):
    """
    Обновление информации о записи на прием.
    Доктор может добавить информацию о приеме (результаты осмотра, назначения и т.д.)
    и изменить статус приема.
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
        
        # Обновляем информацию, если она предоставлена
        if update_data.information is not None:
            # Если уже есть информация, добавляем новую с новой строки
            if db_appointment.information:
                db_appointment.information = db_appointment.information + "\n\n" + update_data.information
            else:
                db_appointment.information = update_data.information
        
        # Обновляем статус, если он предоставлен
        if update_data.status is not None:
            db_appointment.status = update_data.status
        
        # Сохраняем изменения
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
    db: Session = Depends(get_db)
):
    """
    Добавление лекарств пациенту на основе appointment ID.
    Проверяет противопоказания пациента перед назначением.
    Возвращает добавленные лекарства и список конфликтов.
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
        
        # Получаем информацию о докторе из расписания
        db_schedule = db.query(models.Schedule)\
            .filter(models.Schedule.id == db_appointment.schedule_id)\
            .first()
        
        if not db_schedule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Расписание для записи {appointment_id} не найдено"
            )
        
        #Получаем ВСЕ противопоказания пациента
        patient_contradictions = db.query(models.PatientContradiction)\
            .filter(models.PatientContradiction.patient_id == db_appointment.patient_id)\
            .all()
        
        #Получаем ВСЕ лекарства пациента
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
        
        # Получаем противопоказания для всех лекарств пациента из общей таблицы contradiction
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
                # Находим точную причину
                conflict_reasons = []
                
                # Проверяем все возможные причины
                # 1. Прямое противопоказание
                for pc in patient_contradictions:
                    if pc.contradiction == medicament_data.medicament_name:
                        conflict_reasons.append(f"Прямое противопоказание: пациент не переносит '{medicament_data.medicament_name}'")
                
                # 2. Уже принимает это лекарство
                for pm in patient_medicaments:
                    if pm.medicament_name == medicament_data.medicament_name:
                        conflict_reasons.append(f"Пациент уже принимает это лекарство (назначено {pm.start_date})")
                
                # 3. Противопоказание для уже принимаемых лекарств
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
                continue  # Пропускаем это лекарство
            
            # Если проверки прошли успешно - создаем запись
            db_medicament = models.PatientMedicament(
                patient_id=db_appointment.patient_id,
                medicament_name=medicament_data.medicament_name,
                dosage=medicament_data.dosage,
                frequency=medicament_data.frequency,
                start_date=medicament_data.start_date,
                end_date=medicament_data.end_date,
                prescribed_by=f"Dr. {db_schedule.doctor.last_name} {db_schedule.doctor.first_name[0]}.",
                notes=medicament_data.notes
            )
            
            db.add(db_medicament)
            added_medicaments.append(db_medicament)
        
        # Если НИ ОДНО лекарство не было добавлено (все имеют конфликты)
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
        info_text = f"Назначены лекарства: {', '.join(medicament_names)}"

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
            
            # Формируем warning для ответа
            warning_message = f"{len(conflicted_medicaments)} лекарств не были назначены из-за противопоказаний"
            success_message = f"Успешно добавлено {len(added_medicaments)} лекарств"
        else:
            success_message = f"Все {len(added_medicaments)} лекарств успешно добавлены"

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
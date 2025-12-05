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
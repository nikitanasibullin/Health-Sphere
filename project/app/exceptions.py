from functools import wraps
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from typing import Optional, Callable
import logging

logger = logging.getLogger(__name__)

def handle_exceptions(custom_message: Optional[str] = None, rollback: bool = True):
    """
    Декоратор для обработки исключений в эндпоинтах
    
    Параметры:
    - custom_message: дополнительное сообщение для ошибки
    - rollback: выполнять ли rollback при ошибке (по умолчанию True)
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Находим сессию БД в аргументах
            db_session = None
            
            # Ищем в позиционных аргументах
            for arg in args:
                from sqlalchemy.orm import Session
                if isinstance(arg, Session):
                    db_session = arg
                    break
            
            # Ищем в именованных аргументах
            if not db_session:
                for key, value in kwargs.items():
                    from sqlalchemy.orm import Session
                    if isinstance(value, Session):
                        db_session = value
                        break
            
            try:
                return func(*args, **kwargs)
                
            except HTTPException:
                # Преднамеренные HTTP ошибки
                raise
                
            except IntegrityError as e:
                if rollback and db_session:
                    db_session.rollback()
                
                logger.error(f"IntegrityError in {func.__name__}: {str(e)}", exc_info=True)
                
                # Детализируем ошибку
                error_msg = str(e.orig).lower() if e.orig else str(e).lower()
                
                if "unique constraint" in error_msg or "duplicate key" in error_msg:
                    detail = "Нарушение уникальности данных"
                elif "check constraint" in error_msg:
                    detail = "Нарушение проверочного ограничения"
                elif "foreign key" in error_msg:
                    detail = "Нарушение ссылочной целостности"
                elif "not null" in error_msg:
                    detail = "Обязательные поля не заполнены"
                else:
                    detail = "Ошибка целостности данных"
                
                full_detail = f"{custom_message + ': ' if custom_message else ''}{detail}"
                raise HTTPException(status_code=400, detail=full_detail)
                
            except SQLAlchemyError as e:
                if rollback and db_session:
                    db_session.rollback()
                
                logger.error(f"SQLAlchemyError in {func.__name__}: {str(e)}", exc_info=True)
                raise HTTPException(
                    status_code=500,
                    detail=f"{custom_message + ': ' if custom_message else ''}Ошибка базы данных"
                )
                
            except Exception as e:
                if rollback and db_session:
                    db_session.rollback()
                
                logger.error(f"Unexpected error in {func.__name__}: {str(e)}", exc_info=True)
                raise HTTPException(
                    status_code=500,
                    detail=f"{custom_message + ': ' if custom_message else ''}Внутренняя ошибка сервера"
                )
                
        return wrapper
    return decorator
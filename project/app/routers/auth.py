from fastapi import APIRouter, Depends, status, HTTPException, Response
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import database, schemas, models, utils, oauth2

router = APIRouter(tags=['Authentication'])

@router.post("/api/login", response_model=schemas.Token)
def login(
    user_credentials: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(database.get_db)
):
    """
    Вход в систему для пациентов и врачей
    OAuth2PasswordRequestForm возвращает:
    - username (email)
    - password
    """
    # Ищем пользователя по email
    user = db.query(models.User).filter(
        models.User.email == user_credentials.username
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Неверный email или пароль"
        )
    
    # Проверяем пароль
    if not utils.verify(user_credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Неверный email или пароль"
        )
    
    # Создаем токен с данными о типе пользователя
    access_token = oauth2.create_access_token(
        data={
            "user_id": user.id,
            "user_type": user.user_type
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_type": user.user_type
    }

from jose import JWTError, jwt
import datetime
from datetime import timedelta
import schemas
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
import database, models
from sqlalchemy.orm import Session
from config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.datetime.now(datetime.timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_access_token(token: str, credentials_exception):
    """Верификация токена с извлечением данных пользователя"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # Извлекаем данные из токена
        user_id: str = str(payload.get("user_id"))
        user_type: str = payload.get("user_type")  # 'patient' или 'doctor'
        
        if user_id is None or user_type is None:
            raise credentials_exception
        
        # Создаем объект с данными токена
        token_data = schemas.TokenData(id=user_id, user_type=user_type)
        
    except JWTError:
        raise credentials_exception
    
    return token_data

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    """Получение текущего пользователя (общая функция)"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Неверные учетные данные",
        headers={"WWW-Authenticate": "Bearer"}
    )
    
    # Верифицируем токен
    token_data = verify_access_token(token, credentials_exception)
    
    # Ищем пользователя в БД
    user = db.query(models.User).filter(models.User.id == token_data.id).first()
    
    if not user:
        raise credentials_exception
    
    return user

def get_current_patient(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(database.get_db)
):
    """Получение текущего пациента (только для пациентов)"""
    if current_user.user_type != 'patient':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ только для пациентов"
        )
    
    # Ищем профиль пациента
    patient = db.query(models.Patient).filter(models.Patient.user_id == current_user.id).first()
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Профиль пациента не найден"
        )
    
    return patient

def get_current_doctor(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(database.get_db)
):
    """Получение текущего врача (только для врачей)"""
    if current_user.user_type != 'doctor':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ только для врачей"
        )
    
    # Ищем профиль врача
    doctor = db.query(models.Doctor).filter(models.Doctor.user_id == current_user.id).first()
    
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Профиль врача не найден"
        )
    
    return doctor

def get_current_admin(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(database.get_db)
):
    """Пороверка на админа"""
    if current_user.user_type != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ только для администратора"
        )
    
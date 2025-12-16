from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import config
from config import settings

try:
    SQLALCHEMY_DATABASE_URL = f'postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}'
    
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    Base = declarative_base()
    
except Exception as e:
    print(f"Ошибка при создании подключения к БД: {e}")
    # Можно перезапустить приложение или использовать fallback
    raise


#dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        print(f"Ошибка в сессии БД: {e}")
        raise
    finally:
        db.close()
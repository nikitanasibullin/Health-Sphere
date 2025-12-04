import models,schemas
from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from database import get_db
from typing import Optional,List
from sqlalchemy import func

router = APIRouter(
    prefix = "/patient",
    tags=['patient']
)


@router.get("/doctors",response_model=List[schemas.DoctorResponse])
def get_doctors(db: Session = Depends(get_db)):
    doctors= db.query(models.Doctor).all()
    return doctors

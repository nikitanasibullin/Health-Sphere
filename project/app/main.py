from fastapi import FastAPI
from fastapi.params import Body
from random import randrange
import time
from sqlalchemy.orm import Session
import models
#import schemas
#import utils
from database import engine, get_db
#from routers import post, user, auth, vote
from config import settings
from fastapi.middleware.cors import CORSMiddleware

#models.Base.metadata.create_all(bind=engine)

app = FastAPI()

origins=["*"] #every single domain

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
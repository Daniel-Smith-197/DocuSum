from sqlalchemy import Column, Integer, String, Text, DateTime, create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os
from pydantic import BaseModel, ConfigDict
from datetime import datetime

load_dotenv()

engine = create_engine(os.getenv("db_url"))
SessionClass = sessionmaker(bind = engine)
session = SessionClass()
Base = declarative_base()

class Summary(Base):
    __tablename__ = "summaries"
    id = Column(Integer, primary_key = True)
    filename = Column(String)
    sumMode = Column(String)
    summary = Column(Text)
    timestamp = Column(DateTime)
    token_usage = Column(Integer)

class getRec(BaseModel):
    id: int
    filename: str
    sumMode: str
    timestamp: datetime
    token_usage: int
    model_config = ConfigDict(from_attributes = True)

class getSum(BaseModel):
    id: int
    filename: str
    sumMode: str
    summary: str
    timestamp: datetime
    token_usage: int
    model_config = ConfigDict(from_attributes = True)
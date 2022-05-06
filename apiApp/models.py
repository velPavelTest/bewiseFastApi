from sqlalchemy import Column, Integer, String
from sqlalchemy.sql import func
from sqlalchemy.types import DateTime
from db import Base


class Questions(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    origin_id = Column(Integer, index=True, nullable=False)
    source = Column(String())
    question_text = Column(String(), nullable=False)
    answer = Column(String(), nullable=False)
    create_datetime_origin = Column(DateTime)
    create_datetime = Column(DateTime, server_default=func.now())
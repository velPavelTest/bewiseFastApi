from pydantic import BaseModel
from typing import Optional
import datetime


class QuestionOut(BaseModel):
    '''Вид вопроса для выдачи из БД'''
    id: int
    origin_id: int
    source: Optional[str]
    question_text: str
    answer: str
    create_datetime_origin: Optional[datetime.datetime]
    create_datetime: datetime.datetime

    class Config :
        orm_mode = True

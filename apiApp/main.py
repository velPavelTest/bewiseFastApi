from fastapi import FastAPI, Body, Depends, HTTPException

import models
from db import get_db
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse
from questionSources import QuestionSource, jservice
import requests
from dateutil.parser import parse
from pydantic import BaseModel
from typing import Optional
import datetime
from fastapi.responses import JSONResponse

app = FastAPI(title="Random question")

#@task move to schema
class QuestionOut(BaseModel):
    id: int
    origin_id: int
    source: Optional[str]
    question_text: str
    answer: str
    create_datetime_origin: Optional[datetime.datetime]
    create_datetime: datetime.datetime

    class Config :
        orm_mode = True


# @app.get("/")
# def main():
#     return RedirectResponse(url="/docs/")


@app.post(
    "/add_questions/",
    response_description="Add questions",
    description="Add random questions from jservice.io to db",
    response_model=QuestionOut,
)
def add_questions(db: Session = Depends(get_db), questions_num: int = Body(..., embed=True, example=1, gt=0, lt=1000)):
    '''Добавить в БД {questions_num} уникальных вопросов с сервиса jservice. Вернуть последний ранее добавленный вопрос.
    '''

    #При расширении приложения вынести эту функции из add_questions
    def get_questions_from_source(source: QuestionSource, count: int) -> list:
        '''Получение у источника указанное число вопросов, возвращаем чистый json'''
        #@inspect возможно стоит прогнать всё через pydantic, работать с объектами, но кажется для данного случая это излишнее расходование ресурсов.
        r = requests.get(source.api_url, params={source.question_count_get_param: count})
        if r.status_code != 200:
            r.raise_for_status()
        return r.json()

    last_question = db.query(models.Questions).order_by(models.Questions.create_datetime.desc(), models.Questions.id.desc()).first()
    #@answer ba может запрос должен всё же выозращать ответ по результату операции? А последнйи вопрос вынести в отдельный (last_question)
    #@wait anwser возможно стоит вынести всё это в асинхронное выполнение.
    # Из минусов - не сможем дать ответ пользователю, что его запрос не удался.
    source:QuestionSource = jservice
    number_of_attempts:int = 25 # кол-во попыток добиться нужного числа уникальных вопросов. Чтобы не уйти в вечный цикл.
    unique_questions:dict(int, models.Questions) = dict()
    i = 0
    while len(unique_questions) < questions_num and i < number_of_attempts:
        # number_of_attempts раз пытаемся добрать нужное количество вопросов до уникальных.
        # Заодно пытаемся добрать вопросы если у нас запросили больше, чем лимит отдачи источника.
        #@inspect можно повысить шансы на удачу если после n-ой попытке запрашивать не количество не найденных, а больше (limit текущего источника 100).
        new_questions = get_questions_from_source(source, questions_num-len(unique_questions))
        ids = (int(a['id']) for a in new_questions if int(a['id']) not in unique_questions)
        #@test Можно оптимизировать вынеся проверку на существование в уже найденных вопросах до запроса в БД.
        exist_ids = db.query(models.Questions.origin_id).filter(models.Questions.origin_id.in_(ids), models.Questions.source==source.name).all()
        exist_ids = tuple(int(a['origin_id']) for a in exist_ids)
        for q in new_questions:
            origin_id = int(q['id'])
            if origin_id not in exist_ids and origin_id not in unique_questions:
                unique_questions[origin_id] = models.Questions(
                    origin_id=origin_id,
                    source=source.name,
                    question_text=q['question'],
                    answer=q['answer'],
                    create_datetime_origin=parse(q['created_at']),
                )
        i+=1
    if len(unique_questions) == questions_num:
        db.add_all(unique_questions.values())
        db.commit()
        if last_question is None:
            return JSONResponse(content={})
        last_question_pdt: QuestionOut = QuestionOut.from_orm(last_question)
        return last_question_pdt
    else:
        raise HTTPException(status_code=423, detail="Can't find {} new questions. Only {} finded.".format(questions_num, len(unique_questions)))


# @app.get("/last_question/", response_model=QuestionOut,)
# def get_last_quests(db: Session = Depends(get_db)):
#     last_question:models.Questions = db.query(models.Questions).order_by(models.Questions.create_datetime.desc(), models.Questions.id.desc()).first()
#     if last_question is None:
#         return JSONResponse(content={})
#     last_question_pdt:QuestionOut =QuestionOut.from_orm(last_question)
#     return last_question_pdt
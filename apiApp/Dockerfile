FROM python:3.9-slim

WORKDIR /usr/src/app

# переменные окружения для python
# Не создавать *.pyc
ENV PYTHONDONTWRITEBYTECODE 1
# не помещает в буфер потоки stdout и stderr
ENV PYTHONUNBUFFERED 1

#RUN apt-get update && \
#    apt-get install postgresql-dev gcc python3-dev musl-dev

# устанавливаем зависимости
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# копируем содержимое текущей папки в контейнер
COPY . .
FROM python:3

RUN mkdir /app
COPY ../requirements.txt ./app/requirements.txt
WORKDIR /app

run pip install --upgrade pip
run pip install -r requirements.txt

ENV PYTHONPATH "${PYTHONPATH}:app"

#EXPOSE 5000

COPY .. /app
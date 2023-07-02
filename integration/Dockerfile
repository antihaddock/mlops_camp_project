FROM python:3.8.12-slim

RUN pip install pipenv

WORKDIR /application

COPY ["requirements.txt",  "./"]

RUN pip install -r requirements.txt

COPY ["./model.pkl", "./integration_model.py", "./"]

EXPOSE 5000

ENTRYPOINT ["gunicorn", "--bind=0.0.0.0:5000", "integration_model:app"]



FROM python:3.8.12-slim

RUN pip install pipenv

WORKDIR /application

COPY ["Pipfile", "Pipfile.lock", "./"]

RUN pipenv install --system --deploy

COPY ["./model/predict.py", "./"] 

COPY ["./model/pre_process_data.py", "./"] 

EXPOSE 5000

EXPOSE 8000

ENTRYPOINT ["gunicorn", "--bind=0.0.0.0:5000", "predict:app"]


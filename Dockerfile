FROM python:3.8.12-slim

RUN pip install pipenv

WORKDIR /application

COPY ["Pipfile", "Pipfile.lock", "./"]

RUN pipenv install --system --deploy

COPY ["predict.py", "./"] 

COPY ["Models/Dementia-model.bin" , "./Models/"] 

EXPOSE 5000

ENTRYPOINT ["gunicorn", "--bind=0.0.0.0:5000", "predict:app"]
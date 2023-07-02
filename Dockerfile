FROM python:3.8.12-slim

COPY ["requirements.txt", "./"]

RUN pip install -r requirements.txt

WORKDIR /application

COPY ["./model/*.py", "./"]

EXPOSE 5000

EXPOSE 8000

ENTRYPOINT ["gunicorn", "--bind=0.0.0.0:5000", "predict:app"]
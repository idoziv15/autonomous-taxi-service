# dispatcher service dockerfile
FROM python:3.9
WORKDIR /app
COPY ./requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt
COPY ./shared /app/shared
COPY ./services/dispatcher_service /app/
EXPOSE 8002
CMD ["uvicorn", "dispatcher_service:app", "--host", "0.0.0.0", "--port", "8002"]
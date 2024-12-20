# ride service dockerfile
FROM python:3.9
WORKDIR /app
COPY ../../requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt
COPY ./shared /app/shared
COPY ./services/ride_service /app
EXPOSE 8001
CMD ["uvicorn", "ride_service:app", "--host", "0.0.0.0", "--port", "8001"]

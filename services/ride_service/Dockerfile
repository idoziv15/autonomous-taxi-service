FROM python:3.9
WORKDIR /app
COPY ../shared /app/shared
COPY . .
RUN pip install -r ../requirements.txt
EXPOSE 8001
CMD ["uvicorn", "ride_service:app", "--host", "0.0.0.0", "--port", "8001"]

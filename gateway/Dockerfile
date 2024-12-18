FROM python:3.9
WORKDIR /app
COPY ../shared /app/shared
COPY . .
RUN pip install -r ../requirements.txt
EXPOSE 8000
CMD ["uvicorn", "gateway:app", "--host", "0.0.0.0", "--port", "8000"]
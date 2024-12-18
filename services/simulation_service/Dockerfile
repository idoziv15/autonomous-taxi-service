FROM python:3.9
WORKDIR /app
COPY ../shared /app/shared
COPY . .
RUN pip install -r ../requirements.txt
CMD ["python", "simulation.py"]
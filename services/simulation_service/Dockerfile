# simulation service dockerfile
FROM python:3.9
WORKDIR /app
COPY ../../requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt
COPY ../shared /app/shared
COPY ./services/simulation_service /app
CMD ["python", "simulation.py"]
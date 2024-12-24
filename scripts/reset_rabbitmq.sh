#!/bin/bash
echo "Clearing RabbitMQ queues..."
docker exec -it autonomous-taxi-service_rabbitmq_1 rabbitmqctl purge_queue ride_requests

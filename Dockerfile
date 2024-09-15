# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the current directory contents into the container
COPY . .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install Kafka dependencies for Producer/Consumer
RUN pip install confluent-kafka influxdb-client prometheus_client

RUN apt-get update && apt-get install -y iputils-ping

# Make port 8000 available to the world 
EXPOSE 8000

# Define environment variable
ENV FLASK_APP=app.py

# Run app.py when the container launches
CMD ["python", "app.py"]
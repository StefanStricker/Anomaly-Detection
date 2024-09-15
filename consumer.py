import requests
from confluent_kafka import Consumer, KafkaError
import json

# Kafka consumer configuration
conf = {
    'bootstrap.servers': 'kafka:9092',  
    'group.id': 'sensor_data_consumer_group',
    'auto.offset.reset': 'smallest'
}

# API URL where the ML model is hosted
api_url = "http://flask-app:5000/predict"

# Create a Consumer instance
consumer = Consumer(conf)

# Subscribe to the Kafka topic
consumer.subscribe(['sensor_data'])

try:
    while True:
        # Poll for new messages
        msg = consumer.poll(1.0)  # Timeout after 1 second

        if msg is None:
            continue

        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                continue
            else:
                print(f"Error: {msg.error()}")
                break

        # If a message is received, process it
        data = msg.value().decode('utf-8')
        print(f"Received message: {data}")

        # Convert the JSON string to a Python dictionary
        data_dict = json.loads(data)

        # Send the data to the API for prediction
        try:
            response = requests.post(api_url, json=data_dict)
            if response.status_code == 200:
                print(f"Prediction Response: {response.json()}")
            else:
                print(f"Failed to get prediction. Status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Error sending data to the API: {e}")

except KeyboardInterrupt:
    pass

finally:
    # Close down consumer gracefully
    consumer.close()

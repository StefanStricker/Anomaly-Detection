from confluent_kafka import Producer
import time
import random
import json

# Configuration for Kafka
conf = {
    'bootstrap.servers': 'kafka:9092',
    'group.id': 'sensor_data_consumer_group',
    'auto.offset.reset': 'smallest'
}


# Create Producer instance
producer = Producer(conf)

# Delivery report callback to check message delivery
def delivery_report(err, msg):
    if err is not None:
        print(f"Message delivery failed: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}]")

# Generate synthetic data
def generate_synthetic_data():
    data = {
        'timestamp': time.time(),
        'temperature': round(random.gauss(50, 7), 2),
        'humidity': round(random.gauss(50, 8), 2),
        'sound_volume': round(random.gauss(80, 10), 2),
    }
    return data

if __name__ == "__main__":
    topic = "sensor_data"  # Kafka topic name

    while True:
        # Generate synthetic sensor data
        data = generate_synthetic_data()

        # Convert data to JSON format
        data_json = json.dumps(data)

        # Send the data to the Kafka topic
        producer.produce(topic, value=data_json, callback=delivery_report)
        
        # Wait before sending the next message
        time.sleep(2)

        # Poll to handle delivery reports (this ensures messages are sent)
        producer.poll(0)
        
        producer.flush()

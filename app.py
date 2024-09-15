import pickle
import logging
from flask import Flask, request, jsonify
from prometheus_client import start_http_server, Histogram, Counter
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from datetime import datetime
import uuid

# Load model
model = pickle.load(open("ml_model.pkl", "rb"))

# Start application
app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Prometheus metrics
REQUESTS = Counter('flask_app_requests_total', 'Total number of requests')
PREDICTIONS = Counter('flask_app_predictions_total', 'Total number of predictions made')
ERRORS = Counter('flask_app_errors_total', 'Total number of errors encountered')
PREDICTION_TIME = Histogram('flask_app_prediction_processing_time', 'Time taken to process prediction')
ANOMALIES = Counter('flask_app_anomalies_total', 'Total number of anomalies detected')  

# InfluxDB client setup
bucket = "Anomalies"  
org = "f66fff8899cab44c" 
token = "BSFWXW9bg9__lm0FhTTBsOwXRcldwFKHcVnDUWKxuP2RKDLcZTAW7pdWcBtBBY8_E--LggQHkzL6sp7644jhiw=="  
url = "http://influxdb:8086"

client = InfluxDBClient(url=url, token=token, org=org)
write_api = client.write_api(write_options=SYNCHRONOUS)

# Add functionality to obtain model prediction
@app.route("/predict", methods=["POST"])
def predict():
    REQUESTS.inc()  # Increment the total number of requests
    try:
        data = request.get_json()
        app.logger.debug(f"Received data: {data}")

        features = [data["temperature"], data["humidity"], data["sound_volume"]]
        app.logger.debug(f"Extracted features: {features}")

        x_infer = [features]
        app.logger.debug(f"Prepared data for prediction: {x_infer}")

        with PREDICTION_TIME.time():  # Measure time taken for prediction
            y_infer = model.predict(x_infer).tolist()

        app.logger.debug(f"Prediction result: {y_infer}")
        PREDICTIONS.inc()  # Increment the number of predictions made

        # Check if the prediction is an anomaly and increment the anomaly counter
        is_anomaly = y_infer[0] == 1
        if is_anomaly:
            ANOMALIES.inc()

        unique_id = str(uuid.uuid4())  # Generate a unique ID    

        # Log prediction data to InfluxDB
        point = Point("prediction") \
            .tag("is_anomaly", str(is_anomaly)) \
            .field("unique_id", unique_id) \
            .field("temperature", data["temperature"]) \
            .field("humidity", data["humidity"]) \
            .field("sound_volume", data["sound_volume"]) \
            .field("predicted_anomaly", y_infer[0]) \
            .time(datetime.utcnow(), WritePrecision.NS)

        write_api.write(bucket=bucket, org=org, record=point)

        return jsonify({"predicted_anomaly": y_infer})

    except Exception as e:
        app.logger.error(f"Error during prediction: {str(e)}")
        ERRORS.inc()  # Increment the error count
        return jsonify({"error": str(e)}), 500

# Expose metrics endpoint
@app.route('/metrics')
def metrics():
    from prometheus_client import generate_latest
    return generate_latest(), 200

# Start application
if __name__ == "__main__":
    # Start Prometheus client on a different port
    start_http_server(8000)  
    app.run(host="0.0.0.0", port=5000)
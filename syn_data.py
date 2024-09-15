import numpy as np
import pandas as pd

#parameters
num_samples = 1000
temperature_mean = 50
temperature_std = 7
humidity_mean = 50
humidity_std = 8
soundvolume_mean = 80
soundvolume_std = 10

#generate train data

np.random.seed(40)
temperature_data = np.random.normal(temperature_mean, temperature_std, num_samples)
humidity_data = np.random.normal(humidity_mean, humidity_std, num_samples)
sound_volume_data = np.random.normal(soundvolume_mean, soundvolume_std, num_samples)

# Create a DataFrame
data = pd.DataFrame({
    'temperature': temperature_data,
    'humidity': humidity_data,
    'sound_volume': sound_volume_data,
    'anomaly': 0  # Initialize with no anomaly
})

#anomalies
num_anomalies = 50
anomaly_indices = np.random.choice(num_samples, num_anomalies, replace=False)

# Define anomaly conditions
data.loc[anomaly_indices[:20], 'temperature'] += np.random.uniform(20, 30, 20)  # High temperature anomalies
data.loc[anomaly_indices[20:40], 'humidity'] -= np.random.uniform(20, 30, 20)  # Low humidity anomalies
data.loc[anomaly_indices[40:], 'sound_volume'] += np.random.uniform(20, 30, 10)  # High sound volume anomalies

# Mark anomalies
data.loc[anomaly_indices, 'anomaly'] = 1

data.to_csv('synthetic_sensor_data.csv', index=False)
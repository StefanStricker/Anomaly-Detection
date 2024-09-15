import pandas as pd
import numpy as np
import syn_data
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import pickle

# Load the dataset
data = pd.read_csv('synthetic_sensor_data.csv')

# Data separation
y = data["anomaly"]
x = data.drop("anomaly", axis = 1)

# splitting Data
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size = 0.2, random_state = 100)

# creating Model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(x_train, y_train)
model.predict(x_test)
print(model.score(x_test, y_test))

# safe model as pickle file 
with open("ml_model.pkl", "wb") as file:
    pickle.dump(model, file)
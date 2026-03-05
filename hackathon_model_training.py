import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
import joblib

# ==========================================
# STEP 1: GENERATE THE SYNTHETIC DATASET
# ==========================================
print("Generating synthetic climate dataset...")
np.random.seed(42)
num_samples = 5000

# Generating random baseline inputs for the factors (Scale 0 to 100)
data = {
    "car_pooling_rate": np.random.uniform(0, 100, num_samples),
    "carbon_tax_level": np.random.uniform(0, 100, num_samples),
    "public_buses_deployed": np.random.uniform(0, 100, num_samples),
    "fossil_fuel_use": np.random.uniform(0, 100, num_samples),
    "renewable_investment": np.random.uniform(0, 100, num_samples),
    "deforestation_rate": np.random.uniform(0, 100, num_samples),
    "livestock_population": np.random.uniform(0, 100, num_samples),
    "fertilizer_use": np.random.uniform(0, 100, num_samples),
    "carbon_capture_tech": np.random.uniform(0, 100, num_samples),
    "urbanization_rate": np.random.uniform(0, 100, num_samples),
    "air_pollution_control": np.random.uniform(0, 100, num_samples),
}

df = pd.DataFrame(data)

# Formulating the mathematical "ground truth" with random noise
# These formulas represent how the factors actually impact the world
noise = np.random.normal(0, 2, num_samples)

# Example logic: Fossil fuels and deforestation drive carbon up; renewables and capture tech drive it down
df['target_carbon'] = (
    100
    + (df['fossil_fuel_use'] * 0.8)
    + (df['deforestation_rate'] * 0.5)
    + (df['livestock_population'] * 0.3)
    - (df['carbon_capture_tech'] * 0.6)
    - (df['renewable_investment'] * 0.4)
    - (df['public_buses_deployed'] * 0.2)
    + noise
)

# Temperature is highly correlated with carbon, plus urbanization heat traps
df['target_temp'] = 1.2 + ((df['target_carbon'] - 100) * 0.004) + (df['urbanization_rate'] * 0.001)

# Budget goes down with investments, up with taxes
df['target_budget'] = 500 + (df['carbon_tax_level'] * 5) - (df['renewable_investment'] * 3) - (df['carbon_capture_tech'] * 4)

# Support likes clean air and buses, dislikes high taxes
df['target_support'] = 70 - (df['carbon_tax_level'] * 0.2) + (df['public_buses_deployed'] * 0.3) + (df['air_pollution_control'] * 0.4)

# Save the dataset to show judges
df.to_csv("climate_dataset.csv", index=False)
print("Dataset saved as 'climate_dataset.csv'")

# ==========================================
# STEP 2: THE AI MODEL TRAINING PROCESS
# ==========================================
print("\nTraining the AI Model...")

# Split into Features (X) and Targets (y)
X = df.drop(columns=['target_carbon', 'target_temp', 'target_budget', 'target_support'])
y = df[['target_temp', 'target_carbon', 'target_budget', 'target_support']]

# Train-Test Split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Initialize a LIGHTWEIGHT AI Model
model = RandomForestRegressor(
    n_estimators=20,       # Reduced from 100 to 20 trees (Massive size reduction)
    max_depth=5,           # Limits how deep the trees can grow so they don't memorize noise
    min_samples_leaf=4,    # Keeps the branches simple
    random_state=42
)

# Train the model
model.fit(X_train, y_train)

# Test the AI's accuracy
predictions = model.predict(X_test)
mse = mean_squared_error(y_test, predictions)
print(f"Model Training Complete. Mean Squared Error: {mse:.4f}")

# Save the trained AI model WITH COMPRESSION (Level 3 is a great balance)
joblib.dump(model, "climate_ai_model.pkl", compress=3)
print("Lightweight AI Model saved as 'climate_ai_model.pkl'")
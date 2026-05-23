#!/usr/bin/env python3
"""
Create realistic test dataset for pipeline testing
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

np.random.seed(42)
n_records = 5000

# Generate dates over 2 years
start_date = datetime(2023, 1, 1)
dates = [start_date + timedelta(days=np.random.randint(0, 730)) for _ in range(n_records)]

# Generate times with 5 PM peak
probs = [0.02, 0.01, 0.01, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.05, 0.04, 0.04,
         0.04, 0.05, 0.06, 0.07, 0.08, 0.12, 0.08, 0.06, 0.04, 0.03, 0.02, 0.02]
probs = np.array(probs) / np.sum(probs)
hours = np.random.choice(range(24), n_records, p=probs)
minutes = np.random.randint(0, 60, n_records)
times = [f"{h:02d}:{m:02d}" for h, m in zip(hours, minutes)]

# Generate boroughs with realistic distribution
boroughs = np.random.choice(
    ['Brooklyn', 'Queens', 'Manhattan', 'Bronx', 'Staten Island'],
    n_records,
    p=[0.30, 0.25, 0.20, 0.15, 0.10]
)

# Generate contributing factors
factors = np.random.choice([
    'Driver Inattention/Distraction',
    'Failure to Yield Right-of-Way',
    'Following Too Closely',
    'Backing Unsafely',
    'Passing or Lane Usage Improper',
    'Traffic Control Disregarded',
    'Unsafe Speed',
    'Turning Improperly',
    'Passing Too Closely',
    'Fatigued/Drowsy',
    'Unspecified'
], n_records, p=[0.20, 0.15, 0.12, 0.10, 0.08, 0.07, 0.06, 0.05, 0.04, 0.03, 0.10])

# Generate vehicle types
vehicles = np.random.choice([
    'Sedan',
    'Station Wagon/Sport Utility Vehicle',
    'Taxi',
    'Pick-up Truck',
    'Box Truck',
    'Bus',
    'Motorcycle',
    'Bicycle',
    'Unknown'
], n_records, p=[0.35, 0.25, 0.12, 0.10, 0.05, 0.04, 0.03, 0.03, 0.03])

# Generate injuries (most crashes have 0-2 injured)
motorist_injured = np.random.choice([0, 1, 2, 3, 4], n_records, p=[0.65, 0.23, 0.08, 0.03, 0.01])
pedestrian_injured = np.random.choice([0, 1, 2], n_records, p=[0.82, 0.16, 0.02])
cyclist_injured = np.random.choice([0, 1, 2], n_records, p=[0.88, 0.11, 0.01])

# Generate fatalities (rare)
motorist_killed = np.random.choice([0, 1], n_records, p=[0.998, 0.002])
pedestrian_killed = np.random.choice([0, 1], n_records, p=[0.997, 0.003])
cyclist_killed = np.random.choice([0, 1], n_records, p=[0.999, 0.001])

# Calculate totals
total_injured = motorist_injured + pedestrian_injured + cyclist_injured
total_killed = motorist_killed + pedestrian_killed + cyclist_killed

# Generate ZIP codes
zip_codes = np.random.randint(10001, 11697, n_records)

# Generate coordinates (NYC area)
latitudes = np.random.uniform(40.5, 40.9, n_records)
longitudes = np.random.uniform(-74.3, -73.7, n_records)

# Create DataFrame
df = pd.DataFrame({
    'CRASH DATE': [d.strftime('%m/%d/%Y') for d in dates],
    'CRASH TIME': times,
    'BOROUGH': boroughs,
    'ZIP CODE': zip_codes,
    'LATITUDE': latitudes,
    'LONGITUDE': longitudes,
    'CONTRIBUTING FACTOR VEHICLE 1': factors,
    'VEHICLE TYPE CODE 1': vehicles,
    'NUMBER OF PERSONS INJURED': total_injured,
    'NUMBER OF PERSONS KILLED': total_killed,
    'NUMBER OF PEDESTRIANS INJURED': pedestrian_injured,
    'NUMBER OF PEDESTRIANS KILLED': pedestrian_killed,
    'NUMBER OF CYCLIST INJURED': cyclist_injured,
    'NUMBER OF CYCLIST KILLED': cyclist_killed,
    'NUMBER OF MOTORIST INJURED': motorist_injured,
    'NUMBER OF MOTORIST KILLED': motorist_killed,
})

# Save to CSV
output_path = 'test_dataset_crashes.csv'
df.to_csv(output_path, index=False)

print(f"✅ Created test dataset: {output_path}")
print(f"   Records: {len(df):,}")
print(f"   Columns: {len(df.columns)}")
print(f"\n📊 Sample data:")
print(df.head(3))
print(f"\n📈 Statistics:")
print(f"   Total injured: {df['NUMBER OF PERSONS INJURED'].sum():,}")
print(f"   Total killed: {df['NUMBER OF PERSONS KILLED'].sum():,}")
print(f"   Peak hour: {df['CRASH TIME'].str[:2].mode()[0]}:00")
print(f"   Most common borough: {df['BOROUGH'].mode()[0]}")

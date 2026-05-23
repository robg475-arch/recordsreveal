#!/usr/bin/env python3
"""
Generate realistic synthetic police use-of-force dataset
Based on patterns from published research and real-world reports
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Set seed for reproducibility
np.random.seed(42)
random.seed(42)

# Generate 5000 realistic use-of-force incidents over 3 years
n_records = 5000
start_date = datetime(2021, 1, 1)
end_date = datetime(2023, 12, 31)

# Realistic temporal patterns (more incidents evening/night, weekends)
def generate_datetime():
    days = (end_date - start_date).days
    random_day = start_date + timedelta(days=random.randint(0, days))
    
    # Weight towards evening hours (more incidents 6PM-2AM)
    hour_weights = [2, 1, 1, 1, 2, 3, 4, 5, 4, 3, 3, 3,  # 0-11 (midnight-noon)
                    3, 3, 4, 5, 6, 8, 10, 12, 10, 8, 5, 3]  # 12-23 (noon-midnight)
    hour = random.choices(range(24), weights=hour_weights)[0]
    minute = random.randint(0, 59)
    
    return random_day.replace(hour=hour, minute=minute, second=0)

# Generate coordinates (centered on fictional city, similar to Austin TX)
center_lat = 30.2672
center_lon = -97.7431

def generate_location():
    # Cluster incidents in "high-activity" areas with some randomness
    cluster = random.choice(['downtown', 'east', 'north', 'south', 'west'])
    
    if cluster == 'downtown':
        lat = center_lat + np.random.normal(0, 0.02)
        lon = center_lon + np.random.normal(0, 0.02)
    elif cluster == 'east':
        lat = center_lat + np.random.normal(0.05, 0.03)
        lon = center_lon + np.random.normal(0.08, 0.03)
    elif cluster == 'north':
        lat = center_lat + np.random.normal(0.08, 0.03)
        lon = center_lon + np.random.normal(0, 0.03)
    elif cluster == 'south':
        lat = center_lat + np.random.normal(-0.08, 0.03)
        lon = center_lon + np.random.normal(0, 0.03)
    else:  # west
        lat = center_lat + np.random.normal(0, 0.03)
        lon = center_lon + np.random.normal(-0.08, 0.03)
    
    return lat, lon

# Force types (realistic distribution)
force_types = ['Hands-On', 'Taser', 'Chemical Spray', 'Firearm', 'Baton', 'K-9']
force_weights = [45, 25, 15, 5, 7, 3]  # Hands-on most common, firearm least

# Subject demographics (realistic but varied)
races = ['White', 'Black', 'Hispanic', 'Asian', 'Other']
race_weights = [35, 30, 25, 5, 5]

# Incident types
incident_types = ['Traffic Stop', 'Disturbance Call', 'Warrant Service', 'Pursuit', 
                  'Domestic Violence', 'Mental Health Crisis', 'Suspicious Activity']
incident_weights = [20, 25, 10, 8, 12, 15, 10]

# Injury levels
injury_levels = ['None', 'Minor', 'Moderate', 'Severe', 'Fatal']
injury_weights = [50, 30, 12, 6, 2]  # Most incidents: no injury

# Officer experience (years)
def generate_officer_experience():
    # Realistic distribution: mix of new and veteran officers
    return int(np.random.gamma(3, 3))  # Gamma distribution (0-20+ years)

# Generate dataset
data = []
for i in range(n_records):
    incident_dt = generate_datetime()
    lat, lon = generate_location()
    force_type = random.choices(force_types, weights=force_weights)[0]
    race = random.choices(races, weights=race_weights)[0]
    incident_type = random.choices(incident_types, weights=incident_weights)[0]
    injury = random.choices(injury_levels, weights=injury_weights)[0]
    
    # Subject age: realistic distribution (mostly 18-45)
    subject_age = int(np.random.gamma(4, 6) + 18)
    if subject_age > 70:
        subject_age = random.randint(18, 70)
    
    # Officer age: typically 25-55
    officer_age = int(np.random.normal(38, 8))
    officer_age = max(25, min(officer_age, 60))
    
    officer_experience = generate_officer_experience()
    
    # Subject gender
    subject_gender = random.choices(['Male', 'Female'], weights=[75, 25])[0]
    
    # Officer gender
    officer_gender = random.choices(['Male', 'Female'], weights=[85, 15])[0]
    
    # Weapon present (correlates with force type)
    if force_type == 'Firearm':
        weapon_weights = [20, 80]  # 80% weapon present if firearm used
    else:
        weapon_weights = [65, 35]  # 35% weapon present otherwise
    weapon_present = random.choices(['No', 'Yes'], weights=weapon_weights)[0]
    
    # Body camera
    body_camera = random.choices(['Yes', 'No'], weights=[85, 15])[0]
    
    data.append({
        'incident_id': f'UOF-{i+1:05d}',
        'date': incident_dt.strftime('%Y-%m-%d'),
        'time': incident_dt.strftime('%H:%M:%S'),
        'datetime': incident_dt.strftime('%Y-%m-%d %H:%M:%S'),
        'latitude': round(lat, 6),
        'longitude': round(lon, 6),
        'force_type': force_type,
        'incident_type': incident_type,
        'subject_age': subject_age,
        'subject_race': race,
        'subject_gender': subject_gender,
        'officer_age': officer_age,
        'officer_gender': officer_gender,
        'officer_years_experience': officer_experience,
        'weapon_present': weapon_present,
        'injury_level': injury,
        'body_camera_on': body_camera
    })

# Create DataFrame
df = pd.DataFrame(data)

# Sort by datetime
df = df.sort_values('datetime').reset_index(drop=True)

# Save to CSV
output_path = 'police_use_of_force_data.csv'
df.to_csv(output_path, index=False)

print(f"✓ Generated {len(df):,} synthetic use-of-force incidents")
print(f"✓ Date range: {df['date'].min()} to {df['date'].max()}")
print(f"✓ Saved to: {output_path}")
print(f"\nForce type distribution:")
print(df['force_type'].value_counts())
print(f"\nInjury level distribution:")
print(df['injury_level'].value_counts())
print(f"\nIncident type distribution:")
print(df['incident_type'].value_counts())

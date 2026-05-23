#!/usr/bin/env python3
"""
Generate Realistic Test Dataset
Creates synthetic crash data with realistic temporal patterns
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

def generate_realistic_crashes(n_records=5000):
    """Generate synthetic crash data with realistic patterns"""
    
    print("=" * 70)
    print("🏗️  GENERATING REALISTIC TEST DATASET")
    print("=" * 70)
    print(f"Records to generate: {n_records:,}")
    print()
    
    # Define realistic hourly distribution (rush hours are peak)
    # Hour weights: higher = more crashes
    hour_weights = {
        0: 2,   1: 1,   2: 1,   3: 1,   4: 2,   5: 5,    # Late night/early morning
        6: 10,  7: 15,  8: 20,  9: 12, 10: 8,  11: 10,   # Morning rush
        12: 11, 13: 10, 14: 12, 15: 15, 16: 18, 17: 22,  # Afternoon/evening rush
        18: 20, 19: 15, 20: 10, 21: 8,  22: 6,  23: 4    # Evening/night
    }
    
    # Generate timestamps with realistic distribution
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2024, 12, 31)
    date_range = (end_date - start_date).days
    
    timestamps = []
    for _ in range(n_records):
        # Random date
        random_days = random.randint(0, date_range)
        date = start_date + timedelta(days=random_days)
        
        # Weighted random hour (peak at rush hours)
        hour = random.choices(list(hour_weights.keys()), weights=list(hour_weights.values()))[0]
        minute = random.randint(0, 59)
        
        timestamp = date.replace(hour=hour, minute=minute)
        timestamps.append(timestamp)
    
    # Geographic distribution (NYC boroughs)
    boroughs = ['Brooklyn', 'Queens', 'Manhattan', 'Bronx', 'Staten Island']
    borough_weights = [30.7, 24.9, 18.3, 16.0, 10.1]  # Realistic distribution
    
    # Contributing factors
    factors = [
        'Driver Inattention/Distraction',
        'Failure to Yield Right-of-Way',
        'Following Too Closely',
        'Backing Unsafely',
        'Passing or Lane Usage Improper',
        'Unsafe Speed',
        'Traffic Control Disregarded',
        'Turning Improperly',
        'Other Vehicular',
        'Unspecified'
    ]
    factor_weights = [18.7, 15.2, 12.1, 10.5, 8.3, 7.9, 6.4, 5.2, 8.7, 7.0]
    
    # Vehicle types
    vehicle_types = [
        'Sedan',
        'Station Wagon/Sport Utility Vehicle',
        'Taxi',
        'Pick-up Truck',
        'Box Truck',
        'Bus',
        'Bike',
        'Motorcycle',
        'Unknown'
    ]
    vehicle_weights = [28.3, 22.1, 15.4, 12.2, 8.1, 5.3, 4.2, 2.9, 1.5]
    
    # Generate lat/lon for NYC boroughs
    borough_centers = {
        'Brooklyn': (40.6782, -73.9442),
        'Queens': (40.7282, -73.7949),
        'Manhattan': (40.7831, -73.9712),
        'Bronx': (40.8448, -73.8648),
        'Staten Island': (40.5795, -74.1502)
    }
    
    data = []
    for timestamp in timestamps:
        borough = random.choices(boroughs, weights=borough_weights)[0]
        
        # Add some random scatter around borough center
        center_lat, center_lon = borough_centers[borough]
        lat = center_lat + np.random.normal(0, 0.02)  # ~2km scatter
        lon = center_lon + np.random.normal(0, 0.02)
        
        record = {
            'CRASH DATE': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'BOROUGH': borough,
            'LATITUDE': round(lat, 4),
            'LONGITUDE': round(lon, 4),
            'CONTRIBUTING FACTOR VEHICLE 1': random.choices(factors, weights=factor_weights)[0],
            'VEHICLE TYPE CODE 1': random.choices(vehicle_types, weights=vehicle_weights)[0],
            'NUMBER OF PERSONS INJURED': random.choices([0, 1, 2, 3], weights=[70, 20, 7, 3])[0],
            'NUMBER OF PERSONS KILLED': random.choices([0, 1], weights=[99.8, 0.2])[0],
        }
        data.append(record)
    
    df = pd.DataFrame(data)
    
    # Print statistics
    print("✅ Dataset generated!")
    print()
    print("TEMPORAL DISTRIBUTION:")
    df['_hour'] = pd.to_datetime(df['CRASH DATE']).dt.hour
    hourly = df['_hour'].value_counts().sort_index()
    peak_hour = hourly.idxmax()
    print(f"   Peak hour: {peak_hour}:00 ({hourly.max():,} records, {hourly.max()/len(df)*100:.1f}%)")
    print(f"   Hours with data: {len(hourly)}/24")
    print()
    
    print("GEOGRAPHIC DISTRIBUTION:")
    for borough in boroughs:
        count = (df['BOROUGH'] == borough).sum()
        pct = count / len(df) * 100
        print(f"   {borough:20s}: {count:5,} ({pct:5.1f}%)")
    print()
    
    print("CATEGORICAL DISTRIBUTION (Top 3 Factors):")
    top_factors = df['CONTRIBUTING FACTOR VEHICLE 1'].value_counts().head(3)
    for factor, count in top_factors.items():
        pct = count / len(df) * 100
        print(f"   {factor:40s}: {count:5,} ({pct:5.1f}%)")
    print()
    
    return df

if __name__ == "__main__":
    # Generate dataset
    df = generate_realistic_crashes(5000)
    
    # Save to CSV
    output_file = "test_dataset_crashes_realistic.csv"
    df.to_csv(output_file, index=False)
    
    print("=" * 70)
    print(f"✅ SAVED: {output_file}")
    print("=" * 70)
    print()
    print("To use this dataset, run:")
    print(f"  ./run_full_pipeline.sh {output_file} pipeline_output")

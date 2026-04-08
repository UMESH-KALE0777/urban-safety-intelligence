import pandas as pd
import numpy as np
import os

np.random.seed(42)

BANGALORE_ZONES = [
    {"name": "Koramangala",     "lat": 12.9352, "lng": 77.6245, "weight": 0.9},
    {"name": "Shivajinagar",    "lat": 12.9850, "lng": 77.6010, "weight": 1.0},
    {"name": "Whitefield",      "lat": 12.9698, "lng": 77.7500, "weight": 0.8},
    {"name": "BTM Layout",      "lat": 12.9165, "lng": 77.6101, "weight": 0.7},
    {"name": "Indiranagar",     "lat": 12.9784, "lng": 77.6408, "weight": 0.6},
    {"name": "Yeshwanthpur",    "lat": 13.0232, "lng": 77.5481, "weight": 0.9},
    {"name": "Majestic",        "lat": 12.9767, "lng": 77.5713, "weight": 1.0},
    {"name": "Electronic City", "lat": 12.8399, "lng": 77.6770, "weight": 0.5},
    {"name": "Hebbal",          "lat": 13.0354, "lng": 77.5970, "weight": 0.6},
    {"name": "Marathahalli",    "lat": 12.9592, "lng": 77.7009, "weight": 0.7},
    {"name": "HSR Layout",      "lat": 12.9116, "lng": 77.6389, "weight": 0.5},
    {"name": "Jayanagar",       "lat": 12.9250, "lng": 77.5938, "weight": 0.4},
    {"name": "Rajajinagar",     "lat": 12.9944, "lng": 77.5556, "weight": 0.8},
    {"name": "JP Nagar",        "lat": 12.9102, "lng": 77.5936, "weight": 0.4},
    {"name": "Banashankari",    "lat": 12.9255, "lng": 77.5468, "weight": 0.5},
]

CRIME_TYPES = [
    {"type": "theft",        "severity": 2, "prob": 0.30},
    {"type": "robbery",      "severity": 4, "prob": 0.15},
    {"type": "assault",      "severity": 4, "prob": 0.15},
    {"type": "burglary",     "severity": 3, "prob": 0.12},
    {"type": "chain_snatch", "severity": 3, "prob": 0.12},
    {"type": "harassment",   "severity": 3, "prob": 0.10},
    {"type": "vehicle_theft","severity": 2, "prob": 0.06},
]

HOURS = list(range(24))
HOUR_WEIGHTS = [
    0.3, 0.2, 0.2, 0.2, 0.2, 0.3,
    0.4, 0.5, 0.6, 0.7, 0.7, 0.7,
    0.7, 0.7, 0.6, 0.6, 0.7, 0.8,
    0.9, 1.0, 1.0, 0.9, 0.7, 0.5,
]
hour_weights = np.array(HOUR_WEIGHTS)
hour_weights = hour_weights / hour_weights.sum()

records = []
for zone in BANGALORE_ZONES:
    n = int(zone["weight"] * 60) + np.random.randint(10, 30)
    for _ in range(n):
        crime = np.random.choice(
            CRIME_TYPES,
            p=[c["prob"] for c in CRIME_TYPES]
        )
        hour = np.random.choice(HOURS, p=hour_weights)
        lat = zone["lat"] + np.random.normal(0, 0.004)
        lng = zone["lng"] + np.random.normal(0, 0.004)
        records.append({
            "lat":         round(lat, 6),
            "lng":         round(lng, 6),
            "zone":        zone["name"],
            "crime_type":  crime["type"],
            "severity":    crime["severity"],
            "hour":        hour,
            "day_of_week": np.random.randint(0, 7),
            "month":       np.random.randint(1, 13),
            "year":        np.random.choice([2022, 2023, 2024]),
        })

df = pd.DataFrame(records)
os.makedirs("data/raw", exist_ok=True)
df.to_csv("data/raw/crime_data.csv", index=False)
print(f"Generated {len(df)} crime records across {len(BANGALORE_ZONES)} zones")
print(df["crime_type"].value_counts())
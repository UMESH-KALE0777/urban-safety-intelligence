import pandas as pd
import os
from app.utils.logger import get_logger

logger = get_logger(__name__)

RAW_PATH    = os.path.join("data", "raw", "crime_data.csv")
CLEAN_PATH  = os.path.join("data", "processed", "crime_clean.csv")

SAMPLE_DATA = [
    {"lat": 12.9580, "lng": 77.6400, "crime_type": "theft",    "severity": 3},
    {"lat": 12.9940, "lng": 77.5950, "crime_type": "assault",  "severity": 4},
    {"lat": 12.9430, "lng": 77.6180, "crime_type": "robbery",  "severity": 5},
    {"lat": 12.9680, "lng": 77.7200, "crime_type": "theft",    "severity": 3},
    {"lat": 12.9210, "lng": 77.6490, "crime_type": "burglary", "severity": 4},
    {"lat": 13.0180, "lng": 77.5740, "crime_type": "assault",  "severity": 3},
    {"lat": 12.8420, "lng": 77.6600, "crime_type": "theft",    "severity": 2},
    {"lat": 12.9620, "lng": 77.5880, "crime_type": "robbery",  "severity": 4},
    {"lat": 12.9160, "lng": 77.6010, "crime_type": "theft",    "severity": 2},
    {"lat": 13.0350, "lng": 77.5970, "crime_type": "assault",  "severity": 3},
    {"lat": 12.9700, "lng": 77.6100, "crime_type": "theft",    "severity": 2},
    {"lat": 12.9550, "lng": 77.6350, "crime_type": "assault",  "severity": 4},
    {"lat": 12.9450, "lng": 77.6250, "crime_type": "robbery",  "severity": 5},
    {"lat": 12.9600, "lng": 77.6450, "crime_type": "theft",    "severity": 3},
    {"lat": 12.9500, "lng": 77.6300, "crime_type": "burglary", "severity": 4},
]

def load_and_clean() -> pd.DataFrame:
    if os.path.exists(RAW_PATH):
        logger.info(f"Loading real data from {RAW_PATH}")
        df = pd.read_csv(RAW_PATH)
        df = df.dropna(subset=["lat", "lng"])
        df = df[(df["lat"].between(12.80, 13.15)) & (df["lng"].between(77.45, 77.78))]
        if "severity" not in df.columns:
            df["severity"] = 3
        df.to_csv(CLEAN_PATH, index=False)
        logger.info(f"Cleaned data: {len(df)} records saved")
        return df
    else:
        logger.warning("No real data found. Using built-in sample data.")
        return pd.DataFrame(SAMPLE_DATA)
import pandas as pd

def load_crime_data(path="data/raw/crime_dataset.csv"):
    try:
        df = pd.read_csv(path)
        return df
    except Exception as e:
        print("Error loading data:", e)
        return None

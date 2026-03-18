import pandas as pd

def preprocess_crime_data(df):

    # Drop missing values
    df = df.dropna()

    # Convert date
    df["Date Reported"] = pd.to_datetime(
        df["Date Reported"],
        dayfirst=True,
        errors="coerce"
    )

    # Remove invalid dates
    df = df.dropna(subset=["Date Reported"])

    return df

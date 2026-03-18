import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
from src.data.data_loader import load_crime_data
from src.data.data_preprocessing import preprocess_crime_data

def prepare_timeseries(df):

    df["month"] = df["Date Reported"].dt.to_period("M")

    monthly_crime = df.groupby("month").size()

    monthly_crime.index = monthly_crime.index.to_timestamp()

    return monthly_crime


def train_model(series):

    model = ARIMA(series, order=(1,1,1))
    model_fit = model.fit()

    return model_fit


def forecast(model):

    prediction = model.forecast(steps=3)

    prediction.to_csv("data/processed/crime_forecast.csv")

    return prediction


if __name__ == "__main__":
    df = load_crime_data()
    if df is not None:
        df = preprocess_crime_data(df)
        series = prepare_timeseries(df)

    model = train_model(series)

    prediction = forecast(model)

    print("Crime Forecast:")
    print(prediction)
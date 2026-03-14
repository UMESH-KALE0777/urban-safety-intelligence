import pandas as pd
from statsmodels.tsa.arima.model import ARIMA


def load_data():
    df = pd.read_csv("data/raw/crime_dataset.csv")
    return df


def prepare_timeseries(df):

    df["Date Reported"] = pd.to_datetime(df["Date Reported"], dayfirst=True)

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

    df = load_data()

    series = prepare_timeseries(df)

    model = train_model(series)

    prediction = forecast(model)

    print("Crime Forecast:")
    print(prediction)
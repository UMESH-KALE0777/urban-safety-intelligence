import pandas as pd


def load_data(path):
    df = pd.read_csv(path)
    return df


def city_hotspot_analysis(df):

    # count crimes per city
    crime_counts = df.groupby("City").size().reset_index(name="crime_count")

    # assign risk levels
    def risk_level(count):
        if count > 300:
            return "High"
        elif count > 100:
            return "Medium"
        else:
            return "Low"

    crime_counts["risk_level"] = crime_counts["crime_count"].apply(risk_level)

    return crime_counts


if __name__ == "__main__":

    data = load_data("data/raw/crime_dataset.csv")

    hotspots = city_hotspot_analysis(data)

    hotspots.to_csv("data/processed/city_hotspots.csv", index=False)

    print("City hotspot analysis completed.")
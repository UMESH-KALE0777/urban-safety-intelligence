import pandas as pd
import matplotlib.pyplot as plt


def create_chart():

    df = pd.read_csv("data/processed/city_hotspots.csv")

    df = df.sort_values(by="crime_count", ascending=False).head(10)

    plt.figure(figsize=(10,6))
    plt.bar(df["City"], df["crime_count"])

    plt.title("Top 10 Crime Hotspot Cities")
    plt.xlabel("City")
    plt.ylabel("Crime Count")

    plt.xticks(rotation=45)

    plt.tight_layout()

    plt.savefig("crime_hotspots_chart.png")

    print("Crime hotspot chart created!")


if __name__ == "__main__":
    create_chart()
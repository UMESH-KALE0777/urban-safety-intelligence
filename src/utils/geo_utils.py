import pandas as pd
import folium


def create_map():

    df = pd.read_csv("data/processed/hotspot_data.csv")

    m = folium.Map(
        location=[df.latitude.mean(), df.longitude.mean()],
        zoom_start=12
    )

    for _, row in df.iterrows():

        if row['cluster'] == -1:
            color = "gray"
        else:
            color = "red"

        folium.CircleMarker(
            location=[row['latitude'], row['longitude']],
            radius=3,
            color=color,
            fill=True
        ).add_to(m)

    m.save("hotspot_map.html")

    print("Map created successfully!")


if __name__ == "__main__":
    create_map()
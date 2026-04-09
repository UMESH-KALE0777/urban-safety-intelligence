import json
import os
import numpy as np
from sklearn.cluster import DBSCAN
from app.ml.preprocess import load_and_clean
from app.utils.logger import get_logger

logger = get_logger(__name__)

HOTSPOTS_PATH = os.path.join("data", "hotspots", "hotspots.json")

def _risk_label(count: int) -> str:
    if count >= 6:
        return "high"
    elif count >= 3:
        return "medium"
    return "low"

def run_clustering() -> list:
    df = load_and_clean()
    coords = df[["lat", "lng"]].values
    logger.info(f"Running DBSCAN on {len(coords)} points")

    db = DBSCAN(eps=0.009, min_samples=2, algorithm="ball_tree", metric="haversine")
    labels = db.fit_predict(np.radians(coords))
    df = df.copy()
    df["cluster"] = labels

    hotspots = []
    for cluster_id in set(labels):
        if cluster_id == -1:
            continue
        cluster_df = df[df["cluster"] == cluster_id]
        count = len(cluster_df)
        hotspots.append({
            "id":     int(cluster_id),
            "lat":    round(float(cluster_df["lat"].mean()), 6),
            "lng":    round(float(cluster_df["lng"].mean()), 6),
            "count":  count,
            "risk":   _risk_label(count),
            "radius": int(count * 100 + 350),
        })

    os.makedirs(os.path.dirname(HOTSPOTS_PATH), exist_ok=True)
    with open(HOTSPOTS_PATH, "w") as f:
        json.dump(hotspots, f, indent=2)

    logger.info(f"Found {len(hotspots)} hotspot clusters")
    return hotspots

def get_hotspots() -> list:
    if os.path.exists(HOTSPOTS_PATH):
        with open(HOTSPOTS_PATH) as f:
            return json.load(f)
    return run_clustering()
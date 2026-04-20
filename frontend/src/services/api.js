import axios from "axios"

const client = axios.create({
    baseURL: "http://localhost:8000",
    timeout: 10000,
})

export async function fetchSafeRoute({ startLat, startLng, endLat, endLng, timeOfDay }) {
    const res = await client.post("/api/routes/safe", {
        start_lat: startLat,
        start_lng: startLng,
        end_lat: endLat,
        end_lng: endLng,
        time_of_day: timeOfDay,
    })
    return res.data.routes
}

export async function fetchHotspots() {
    const res = await client.get("/api/hotspots/")
    return res.data.hotspots
}
import { useState } from "react"
import { fetchSafeRoute } from "../services/api"

export function useRoutes() {
    const [routes, setRoutes] = useState([])
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState(null)

    const getRoutes = async ({ start, end, timeOfDay }) => {
        setLoading(true)
        setError(null)
        try {
            const data = await fetchSafeRoute({
                startLat: start.lat,
                startLng: start.lng,
                endLat: end.lat,
                endLng: end.lng,
                timeOfDay,
            })
            setRoutes(data)
        } catch (err) {
            setError("Could not fetch routes. Is the backend running?")
        } finally {
            setLoading(false)
        }
    }

    return { routes, loading, error, getRoutes }
}
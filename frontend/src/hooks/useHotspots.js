import { useState, useEffect } from "react"
import { fetchHotspots } from "../services/api"

export function useHotspots() {
    const [hotspots, setHotspots] = useState([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)

    useEffect(() => {
        fetchHotspots()
            .then(setHotspots)
            .catch(err => setError(err.message))
            .finally(() => setLoading(false))
    }, [])

    return { hotspots, loading, error }
}
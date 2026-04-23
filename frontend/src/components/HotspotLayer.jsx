import { useEffect, useRef } from "react"
import L from "leaflet"

const COLORS = { high: "#e8453c", medium: "#fbbc04", low: "#34a853" }
const OPACITY = { high: 0.25, medium: 0.18, low: 0.12 }

export default function HotspotLayer({ map, hotspots }) {
    const layersRef = useRef([])

    useEffect(() => {
        if (!map || !hotspots.length) return
        layersRef.current.forEach(l => map.removeLayer(l))
        layersRef.current = hotspots.map(h =>
            L.circle([h.lat, h.lng], {
                radius: h.radius,
                color: COLORS[h.risk],
                fillColor: COLORS[h.risk],
                fillOpacity: OPACITY[h.risk],
                weight: 1, opacity: 0.5,
            })
                .addTo(map)
                .bindTooltip(`${h.risk.toUpperCase()} risk · ${h.count} incidents`, { sticky: true })
        )
        return () => layersRef.current.forEach(l => map.removeLayer(l))
    }, [map, hotspots])

    return null
}
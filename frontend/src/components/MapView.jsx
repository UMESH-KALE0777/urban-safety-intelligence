import "leaflet/dist/leaflet.css"
import { useEffect, useRef, useState } from "react"
import L from "leaflet"
import HotspotLayer from "./HotspotLayer"
import RoutePanel from "./RoutePanel"
import SafetyLegend from "./SafetyLegend"

const ROUTE_COLORS = ["#1a73e8", "#fbbc04", "#9e9e9e"]
const ROUTE_WEIGHTS = [5, 3, 2.5]
const ROUTE_DASH = [null, "8 5", "4 4"]

export default function MapView({ routes, hotspots, start, end }) {
    const mapRef = useRef(null)
    const mapObj = useRef(null)
    const routeRefs = useRef([])
    const markerRefs = useRef([])
    const [selectedIdx, setSelectedIdx] = useState(0)

    useEffect(() => {
        mapObj.current = L.map(mapRef.current, { zoomControl: true })
            .setView([12.9716, 77.5946], 12)
        L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
            attribution: "© OpenStreetMap contributors", maxZoom: 18,
        }).addTo(mapObj.current)
        return () => mapObj.current.remove()
    }, [])

    useEffect(() => {
        const map = mapObj.current
        if (!map || !routes.length) return

        routeRefs.current.forEach(l => map.removeLayer(l))
        markerRefs.current.forEach(l => map.removeLayer(l))
        routeRefs.current = []
        markerRefs.current = []

        routes.forEach((r, i) => {
            const pts = r.waypoints.map(wp => [wp.lat, wp.lng])
            const line = L.polyline(pts, {
                color: ROUTE_COLORS[i],
                weight: ROUTE_WEIGHTS[i],
                dashArray: ROUTE_DASH[i],
                opacity: 0.85,
            }).addTo(map)
            routeRefs.current.push(line)
        })

        if (start) {
            const m = L.circleMarker([start.lat, start.lng], {
                radius: 9, fillColor: "#1a73e8", color: "#fff", weight: 2, fillOpacity: 1,
            }).addTo(map).bindTooltip("Start", { permanent: true, direction: "top" })
            markerRefs.current.push(m)
        }

        if (end) {
            const m = L.circleMarker([end.lat, end.lng], {
                radius: 9, fillColor: "#e8453c", color: "#fff", weight: 2, fillOpacity: 1,
            }).addTo(map).bindTooltip("End", { permanent: true, direction: "top" })
            markerRefs.current.push(m)
        }

        const allPts = routes.flatMap(r => r.waypoints.map(wp => [wp.lat, wp.lng]))
        map.fitBounds(L.latLngBounds(allPts).pad(0.15))
    }, [routes, start, end])

  return (
    <div style={{ position: "absolute", top: 0, left: 0, right: 0, bottom: 0 }}>
      <div ref={mapRef} style={{ width: "100%", height: "100%" }} />
      <HotspotLayer map={mapObj.current} hotspots={hotspots} />
      <RoutePanel routes={routes} selectedIdx={selectedIdx} onSelect={setSelectedIdx} />
      <SafetyLegend />
    </div>
  )
}
import "leaflet/dist/leaflet.css"
import { useEffect, useRef, useState } from "react"
import L from "leaflet"
import HotspotLayer from "./HotspotLayer"
import RoutePanel from "./RoutePanel"
import SafetyLegend from "./SafetyLegend"
import LoadingSpinner from "./LoadingSpinner"

const ROUTE_COLORS = ["#3b82f6", "#f59e0b", "#9e9e9e"]
const ROUTE_WEIGHTS = [5, 3.5, 2.5]
const ROUTE_DASH = [null, "8 5", "4 4"]

export default function MapView({ routes, hotspots, start, end, loading, womenSafety }) {
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
                opacity: i === selectedIdx ? 1 : 0.5,
                lineCap: "round",
                lineJoin: "round",
            }).addTo(map)
            line.bindTooltip(
                `${r.name} · ${r.distance_km}km · Risk: ${r.risk_score}`,
                { sticky: true }
            )
            routeRefs.current.push(line)
        })

        if (start) {
            const startIcon = L.divIcon({
                html: `<div style="width:14px;height:14px;border-radius:50%;
          background:#3b82f6;border:3px solid white;
          box-shadow:0 2px 6px rgba(0,0,0,0.3)"></div>`,
                iconSize: [14, 14], iconAnchor: [7, 7], className: "",
            })
            markerRefs.current.push(
                L.marker([start.lat, start.lng], { icon: startIcon })
                    .addTo(map).bindTooltip("Start", {
                        permanent: true, direction: "top",
                        className: ""
                    })
            )
        }

        if (end) {
            const endIcon = L.divIcon({
                html: `<div style="width:14px;height:14px;border-radius:50%;
          background:#ef4444;border:3px solid white;
          box-shadow:0 2px 6px rgba(0,0,0,0.3)"></div>`,
                iconSize: [14, 14], iconAnchor: [7, 7], className: "",
            })
            markerRefs.current.push(
                L.marker([end.lat, end.lng], { icon: endIcon })
                    .addTo(map).bindTooltip("End", {
                        permanent: true, direction: "top",
                        className: ""
                    })
            )
        }

        const allPts = routes.flatMap(r => r.waypoints.map(wp => [wp.lat, wp.lng]))
        map.fitBounds(L.latLngBounds(allPts).pad(0.18))
    }, [routes, start, end])

    return (
        <div style={{ position: "absolute", top: 0, left: 0, right: 0, bottom: 0 }}>
            <div ref={mapRef} style={{ width: "100%", height: "100%" }} />
            {loading && <LoadingSpinner message="Finding safest route..." />}
            <HotspotLayer map={mapObj.current} hotspots={hotspots} />
            <RoutePanel
                routes={routes}
                selectedIdx={selectedIdx}
                onSelect={setSelectedIdx}
                womenSafety={womenSafety}
            />
            <SafetyLegend />
        </div>
    )
}
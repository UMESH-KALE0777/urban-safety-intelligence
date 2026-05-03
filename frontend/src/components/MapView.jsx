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
        mapObj.current = L.map(mapRef.current, { zoomControl: false })
            .setView([12.9716, 77.5946], 13)

        L.tileLayer("https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png", {
            attribution: "© OpenStreetMap © CARTO",
            maxZoom: 19,
        }).addTo(mapObj.current)

        L.control.zoom({ position: "bottomright" }).addTo(mapObj.current)

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
                opacity: i === 0 ? 1 : 0.55,
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
                html: `<div style="width:16px;height:16px;border-radius:50%;
          background:#3b82f6;border:3px solid white;
          box-shadow:0 2px 8px rgba(59,130,246,0.5)"></div>`,
                iconSize: [16, 16], iconAnchor: [8, 8], className: "",
            })
            markerRefs.current.push(
                L.marker([start.lat, start.lng], { icon: startIcon })
                    .addTo(map)
                    .bindTooltip("📍 Start", { permanent: true, direction: "top" })
            )
        }

        if (end) {
            const endIcon = L.divIcon({
                html: `<div style="width:16px;height:16px;border-radius:50%;
          background:#ef4444;border:3px solid white;
          box-shadow:0 2px 8px rgba(239,68,68,0.5)"></div>`,
                iconSize: [16, 16], iconAnchor: [8, 8], className: "",
            })
            markerRefs.current.push(
                L.marker([end.lat, end.lng], { icon: endIcon })
                    .addTo(map)
                    .bindTooltip("🏁 End", { permanent: true, direction: "top" })
            )
        }

        const allPts = routes.flatMap(r => r.waypoints.map(wp => [wp.lat, wp.lng]))
        map.fitBounds(L.latLngBounds(allPts).pad(0.18))
    }, [routes, start, end])

    return (
        <div style={{ position: "absolute", top: 0, left: 0, right: 0, bottom: 0 }}>
            <div ref={mapRef} style={{ width: "100%", height: "100%" }} />
            {loading && <LoadingSpinner message="Analyzing safe routes..." />}
            <HotspotLayer map={mapObj.current} hotspots={hotspots} />
            <RoutePanel
                routes={routes}
                selectedIdx={selectedIdx}
                onSelect={setSelectedIdx}
                womenSafety={womenSafety}
            />
            <SafetyLegend />

            {/* Empty state */}
            {!routes.length && !loading && (
                <div style={{
                    position: "absolute", top: "50%", left: "50%",
                    transform: "translate(-50%, -50%)", zIndex: 1000,
                    background: "rgba(255,255,255,0.95)", borderRadius: 16,
                    padding: "24px 32px", textAlign: "center",
                    boxShadow: "0 4px 24px rgba(0,0,0,0.10)",
                    border: "1px solid #e2e8f0", backdropFilter: "blur(8px)"
                }}>
                    <div style={{ fontSize: 36, marginBottom: 10 }}>🛡️</div>
                    <p style={{ fontSize: 14, fontWeight: 700, color: "#0f172a", marginBottom: 4 }}>
                        Urban Safety Intelligence
                    </p>
                    <p style={{ fontSize: 12, color: "#64748b", maxWidth: 220 }}>
                        Select your start and destination above to find the safest route through Bangalore
                    </p>
                </div>
            )}
        </div>
    )
}
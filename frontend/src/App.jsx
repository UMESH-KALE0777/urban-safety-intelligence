import { useState } from "react"
import MapView from "./components/MapView"
import SearchBar from "./components/SearchBar"
import { useHotspots } from "./hooks/useHotspots"
import { useRoutes } from "./hooks/useRoutes"

export default function App() {
  const [start, setStart] = useState(null)
  const [end, setEnd] = useState(null)
  const [womenSafety, setWomenSafety] = useState(false)

  const { hotspots } = useHotspots()
  const { routes, loading, getRoutes } = useRoutes()

  const handleSearch = ({ start, end, timeOfDay }) => {
    setStart(start)
    setEnd(end)
    getRoutes({ start, end, timeOfDay })
  }

  return (
    <div style={{
      display: "flex", flexDirection: "column",
      height: "100vh", width: "100vw", overflow: "hidden"
    }}>

      {/* Header */}
      <div style={{
        background: "#0f172a", padding: "0 20px", height: 52,
        display: "flex", alignItems: "center", justifyContent: "space-between",
        flexShrink: 0, boxShadow: "0 1px 0 rgba(255,255,255,0.06)"
      }}>

        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <div style={{
            width: 32, height: 32, background: "linear-gradient(135deg,#3b82f6,#1d4ed8)",
            borderRadius: 9, display: "flex", alignItems: "center",
            justifyContent: "center", fontSize: 16,
            boxShadow: "0 2px 8px rgba(59,130,246,0.4)"
          }}>🛡️</div>
          <div>
            <div style={{
              color: "white", fontSize: 14, fontWeight: 700,
              letterSpacing: "-0.01em"
            }}>Urban Safety Intelligence</div>
            <div style={{ color: "#475569", fontSize: 10, fontWeight: 500 }}>
              Bangalore · ML-Powered Route Safety
            </div>
          </div>
        </div>

        {/* Women Safety Toggle */}
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <div style={{ textAlign: "right" }}>
            <div style={{
              fontSize: 11, color: womenSafety ? "#f472b6" : "#64748b",
              fontWeight: 600, transition: "color 0.2s"
            }}>
              Women's Safety
            </div>
            <div style={{ fontSize: 9, color: "#475569" }}>
              {womenSafety ? "Active — safer routing on" : "Toggle for safer routing"}
            </div>
          </div>
          <div onClick={() => setWomenSafety(!womenSafety)} style={{
            width: 44, height: 24, borderRadius: 12,
            background: womenSafety
              ? "linear-gradient(135deg,#ec4899,#be185d)"
              : "#1e293b",
            cursor: "pointer", position: "relative",
            transition: "background 0.25s",
            border: "1px solid " + (womenSafety ? "#f472b6" : "#334155"),
            boxShadow: womenSafety ? "0 0 12px rgba(236,72,153,0.4)" : "none",
          }}>
            <div style={{
              position: "absolute", top: 3,
              left: womenSafety ? 23 : 3, width: 16, height: 16,
              borderRadius: "50%", background: "white",
              transition: "left 0.25s",
              boxShadow: "0 1px 4px rgba(0,0,0,0.3)"
            }} />
          </div>
        </div>
      </div>

      {/* Search */}
      <SearchBar onSearch={handleSearch} loading={loading} womenSafety={womenSafety} />

      {/* Map */}
      <div style={{ flex: 1, position: "relative", overflow: "hidden" }}>
        <MapView
          routes={routes}
          hotspots={hotspots}
          start={start}
          end={end}
          loading={loading}
          womenSafety={womenSafety}
        />
      </div>
    </div>
  )
}
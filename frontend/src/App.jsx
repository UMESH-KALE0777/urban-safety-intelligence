import { useState } from "react"
import MapView from "./components/MapView"
import SearchBar from "./components/SearchBar"
import { useHotspots } from "./hooks/useHotspots"
import { useRoutes } from "./hooks/useRoutes"

export default function App() {
  const [start, setStart] = useState(null)
  const [end, setEnd] = useState(null)
  const [womenSafety, setWomenSafety] = useState(false)
  const [timeOfDay, setTimeOfDay] = useState("day")

  const { hotspots } = useHotspots()
  const { routes, loading, getRoutes } = useRoutes()

  const handleSearch = ({ start, end, timeOfDay }) => {
    setStart(start)
    setEnd(end)
    setTimeOfDay(timeOfDay)
    getRoutes({ start, end, timeOfDay })
  }

  return (
    <div style={{
      display: "flex", flexDirection: "column",
      height: "100vh", width: "100vw", overflow: "hidden",
      background: "#f8f9fa"
    }}>

      {/* Top Header */}
      <div style={{
        background: "#0f172a", padding: "0 20px",
        height: 52, display: "flex", alignItems: "center",
        justifyContent: "space-between", flexShrink: 0,
        boxShadow: "0 1px 3px rgba(0,0,0,0.3)"
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <div style={{
            width: 28, height: 28, background: "#3b82f6",
            borderRadius: 8, display: "flex", alignItems: "center",
            justifyContent: "center", fontSize: 14
          }}>🛡️</div>
          <div>
            <div style={{
              color: "white", fontSize: 14, fontWeight: 700,
              letterSpacing: "0.01em"
            }}>Urban Safety Intelligence</div>
            <div style={{ color: "#64748b", fontSize: 10 }}>Bangalore · Powered by ML</div>
          </div>
        </div>

        {/* Women Safety Toggle */}
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <span style={{
            fontSize: 11, color: womenSafety ? "#f472b6" : "#64748b",
            fontWeight: 500, transition: "color 0.2s"
          }}>
            👩 Women's Safety
          </span>
          <div onClick={() => setWomenSafety(!womenSafety)}
            style={{
              width: 40, height: 22, borderRadius: 11,
              background: womenSafety ? "#ec4899" : "#334155",
              cursor: "pointer", position: "relative", transition: "background 0.2s"
            }}>
            <div style={{
              position: "absolute", top: 3,
              left: womenSafety ? 21 : 3, width: 16, height: 16,
              borderRadius: "50%", background: "white",
              transition: "left 0.2s", boxShadow: "0 1px 3px rgba(0,0,0,0.2)"
            }} />
          </div>
        </div>
      </div>

      {/* Search Bar */}
      <SearchBar onSearch={handleSearch} loading={loading} womenSafety={womenSafety} />

      {/* Map Area */}
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
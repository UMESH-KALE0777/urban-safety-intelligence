import { useState } from "react"
import MapView from "./components/MapView"
import SearchBar from "./components/SearchBar"
import LoadingSpinner from "./components/LoadingSpinner"
import { useHotspots } from "./hooks/useHotspots"
import { useRoutes } from "./hooks/useRoutes"

export default function App() {
  const [start, setStart] = useState(null)
  const [end, setEnd]     = useState(null)

  const { hotspots }                   = useHotspots()
  const { routes, loading, getRoutes } = useRoutes()

  const handleSearch = ({ start, end, timeOfDay }) => {
    setStart(start)
    setEnd(end)
    getRoutes({ start, end, timeOfDay })
  }

  return (
    <div style={{ display: "flex", flexDirection: "column",
      height: "100vh", width: "100vw", overflow: "hidden" }}>
      <div style={{ background: "#1a73e8", padding: "10px 16px",
        color: "white", fontSize: 15, fontWeight: 700,
        letterSpacing: "0.02em", flexShrink: 0 }}>
        Urban Safety Intelligence — Bangalore
      </div>
      <SearchBar onSearch={handleSearch} loading={loading} />
      {loading && <LoadingSpinner message="Finding safest route..." />}
      <div style={{ flex: 1, position: "relative", overflow: "hidden" }}>
        <MapView routes={routes} hotspots={hotspots} start={start} end={end} />
      </div>
    </div>
  )
}
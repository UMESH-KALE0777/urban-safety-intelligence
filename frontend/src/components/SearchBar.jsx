import { useState } from "react"
import { BANGALORE_LOCATIONS } from "../constants/locations"

export default function SearchBar({ onSearch, loading }) {
    const locations = Object.keys(BANGALORE_LOCATIONS)
    const [from, setFrom] = useState("Koramangala")
    const [to, setTo] = useState("MG Road")
    const [time, setTime] = useState("day")

    const handleSearch = () => {
        if (from === to) return alert("Start and destination cannot be the same.")
        onSearch({
            start: BANGALORE_LOCATIONS[from],
            end: BANGALORE_LOCATIONS[to],
            timeOfDay: time,
            fromName: from,
            toName: to,
        })
    }

    return (
        <div style={{
            display: "flex", gap: 10, padding: "12px 16px",
            background: "white", borderBottom: "1px solid #e5e5e5",
            flexWrap: "wrap", alignItems: "center", zIndex: 100
        }}>
            <div style={groupStyle}>
                <label style={labelStyle}>From</label>
                <select value={from} onChange={e => setFrom(e.target.value)} style={selStyle}>
                    {locations.map(l => <option key={l}>{l}</option>)}
                </select>
            </div>
            <div style={groupStyle}>
                <label style={labelStyle}>To</label>
                <select value={to} onChange={e => setTo(e.target.value)} style={selStyle}>
                    {locations.map(l => <option key={l}>{l}</option>)}
                </select>
            </div>
            <div style={groupStyle}>
                <label style={labelStyle}>Time</label>
                <select value={time} onChange={e => setTime(e.target.value)} style={selStyle}>
                    <option value="day">Daytime</option>
                    <option value="evening">Evening</option>
                    <option value="night">Night</option>
                </select>
            </div>
            <button onClick={handleSearch} disabled={loading} style={{
                ...btnStyle, opacity: loading ? 0.7 : 1,
                cursor: loading ? "not-allowed" : "pointer"
            }}>
                {loading ? "Finding..." : "Find Safe Route"}
            </button>
        </div>
    )
}

const groupStyle = { display: "flex", flexDirection: "column", gap: 3 }
const labelStyle = {
    fontSize: 10, color: "#888", fontWeight: 600,
    textTransform: "uppercase", letterSpacing: "0.05em"
}
const selStyle = {
    padding: "8px 12px", borderRadius: 8,
    border: "1px solid #ddd", fontSize: 13, background: "#fafafa",
    cursor: "pointer", minWidth: 140
}
const btnStyle = {
    padding: "8px 20px", borderRadius: 8, border: "none",
    background: "#1a73e8", color: "white", fontSize: 13,
    fontWeight: 600, marginTop: 12
}
const STYLES = {
    safest: { bg: "#e6f4ea", color: "#1e6e3c", label: "Safest" },
    fastest: { bg: "#fff3e0", color: "#9a5000", label: "Fastest" },
    alternate: { bg: "#fce8e6", color: "#a33333", label: "Alternate" },
}

export default function RoutePanel({ routes, selectedIdx, onSelect }) {
    if (!routes.length) return null

    return (
        <div style={{
            position: "absolute", top: 12, right: 12, width: 240,
            background: "white", borderRadius: 12, border: "1px solid #e5e5e5",
            padding: 14, zIndex: 1000, boxShadow: "0 2px 12px rgba(0,0,0,0.08)"
        }}>
            <p style={{ fontSize: 13, fontWeight: 600, marginBottom: 10, color: "#333" }}>
                Route options
            </p>
            {routes.map((r, i) => {
                const s = STYLES[r.label] || STYLES.alternate
                const isSelected = i === selectedIdx
                return (
                    <div key={i} onClick={() => onSelect(i)} style={{
                        border: isSelected ? "1.5px solid #1a73e8" : "1px solid #eee",
                        borderRadius: 8, padding: "10px 12px", marginBottom: 8,
                        cursor: "pointer", transition: "border 0.15s",
                    }}>
                        <div style={{
                            display: "flex", justifyContent: "space-between",
                            alignItems: "center", marginBottom: 4
                        }}>
                            <span style={{ fontSize: 12, fontWeight: 600, color: "#333" }}>
                                {r.name}
                            </span>
                            <span style={{
                                fontSize: 10, padding: "2px 8px", borderRadius: 99,
                                background: s.bg, color: s.color, fontWeight: 600
                            }}>
                                {s.label}
                            </span>
                        </div>
                        <div style={{ fontSize: 11, color: "#888", marginBottom: 6 }}>
                            {r.distance_km} km · ~{r.duration_min} min · Risk: {r.risk_score}
                        </div>
                        <div style={{ height: 4, borderRadius: 2, background: "#f0f0f0" }}>
                            <div style={{
                                height: "100%", borderRadius: 2,
                                width: `${r.safety_pct}%`,
                                background: i === 0 ? "#34a853" : i === 1 ? "#fbbc04" : "#e8453c",
                            }} />
                        </div>
                    </div>
                )
            })}
        </div>
    )
}
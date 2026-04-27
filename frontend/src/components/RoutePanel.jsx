const STYLES = {
  safest:    { bg: "#f0fdf4", border: "#86efac", badge: "#16a34a", label: "Safest",    icon: "🛡️" },
  fastest:   { bg: "#fffbeb", border: "#fcd34d", badge: "#d97706", label: "Fastest",   icon: "⚡" },
  alternate: { bg: "#fef2f2", border: "#fca5a5", badge: "#dc2626", label: "Alternate", icon: "↗️" },
}

function SafetyCircle({ pct }) {
  const color = pct >= 70 ? "#16a34a" : pct >= 40 ? "#d97706" : "#dc2626"
  return (
    <div style={{ textAlign: "center" }}>
      <div style={{ width: 44, height: 44, borderRadius: "50%",
        border: `3px solid ${color}`, display: "flex", flexDirection: "column",
        alignItems: "center", justifyContent: "center",
        background: `${color}11` }}>
        <span style={{ fontSize: 13, fontWeight: 700, color, lineHeight: 1 }}>{pct}</span>
        <span style={{ fontSize: 8, color, lineHeight: 1 }}>SAFE</span>
      </div>
    </div>
  )
}

export default function RoutePanel({ routes, selectedIdx, onSelect, womenSafety }) {
  if (!routes.length) return null

  return (
    <div className="slide-in" style={{ position: "absolute", top: 12, right: 12,
      width: 260, background: "white", borderRadius: 16,
      border: "1px solid #e2e8f0", padding: 14, zIndex: 1000,
      boxShadow: "0 4px 24px rgba(0,0,0,0.10)" }}>

      <div style={{ display: "flex", alignItems: "center",
        justifyContent: "space-between", marginBottom: 12 }}>
        <p style={{ fontSize: 13, fontWeight: 700, color: "#0f172a" }}>
          Route Options
        </p>
        {womenSafety && (
          <span style={{ fontSize: 10, padding: "2px 8px", borderRadius: 99,
            background: "#fdf2f8", color: "#be185d", fontWeight: 600 }}>
            👩 Safety Mode
          </span>
        )}
      </div>

      {routes.map((r, i) => {
        const s = STYLES[r.label] || STYLES.alternate
        const isSelected = i === selectedIdx
        return (
          <div key={i} onClick={() => onSelect(i)} className="fade-in"
            style={{ border: `1.5px solid ${isSelected ? "#3b82f6" : s.border}`,
              borderRadius: 12, padding: "10px 12px", marginBottom: 8,
              cursor: "pointer", background: isSelected ? "#eff6ff" : s.bg,
              transition: "all 0.15s", }}>

            <div style={{ display: "flex", justifyContent: "space-between",
              alignItems: "flex-start", gap: 8 }}>
              <div style={{ flex: 1 }}>
                <div style={{ display: "flex", alignItems: "center",
                  gap: 6, marginBottom: 4 }}>
                  <span style={{ fontSize: 11, fontWeight: 700, color: "#0f172a" }}>
                    {s.icon} {r.name}
                  </span>
                  <span style={{ fontSize: 9, padding: "1px 6px", borderRadius: 99,
                    background: s.badge + "22", color: s.badge, fontWeight: 700 }}>
                    {s.label}
                  </span>
                </div>
                <div style={{ fontSize: 11, color: "#64748b", marginBottom: 6 }}>
                  📍 {r.distance_km} km &nbsp;·&nbsp; ⏱ ~{r.duration_min} min
                </div>
                <div style={{ fontSize: 10, color: "#94a3b8", marginBottom: 6 }}>
                  Risk score: {r.risk_score}
                </div>
                {/* Safety bar */}
                <div style={{ height: 3, borderRadius: 2, background: "#e2e8f0" }}>
                  <div style={{ height: "100%", borderRadius: 2,
                    width: `${r.safety_pct}%`,
                    background: i === 0 ? "#16a34a" : i === 1 ? "#d97706" : "#dc2626",
                    transition: "width 0.5s ease" }} />
                </div>
              </div>
              <SafetyCircle pct={r.safety_pct} />
            </div>
          </div>
        )
      })}

      {/* Stats footer */}
      <div style={{ marginTop: 10, paddingTop: 10, borderTop: "1px solid #f1f5f9",
        display: "flex", justifyContent: "space-between" }}>
        <span style={{ fontSize: 10, color: "#94a3b8" }}>
          🔴 {routes[0]?.risk_score === 0 ? "Low" : "Active"} crime zone nearby
        </span>
        <span style={{ fontSize: 10, color: "#3b82f6", fontWeight: 500, cursor: "pointer" }}
          onClick={() => navigator.clipboard.writeText(window.location.href)}>
          Share route ↗
        </span>
      </div>
    </div>
  )
}
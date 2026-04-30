export default function SafetyLegend() {
    return (
        <div style={{
            position: "absolute", bottom: 28, left: 12,
            background: "rgba(255,255,255,0.95)", borderRadius: 12,
            padding: "10px 14px", border: "1px solid #e2e8f0",
            zIndex: 1000, fontSize: 11,
            boxShadow: "0 2px 8px rgba(0,0,0,0.08)",
            backdropFilter: "blur(8px)"
        }}>
            <p style={{ fontWeight: 700, marginBottom: 8, color: "#0f172a", fontSize: 11 }}>
                🗺️ Map Legend
            </p>
            {[
                { color: "#ef4444", label: "High risk zone" },
                { color: "#f59e0b", label: "Medium risk zone" },
                { color: "#22c55e", label: "Low risk zone" },
            ].map(item => (
                <div key={item.label} style={{
                    display: "flex", alignItems: "center",
                    gap: 8, marginBottom: 5
                }}>
                    <div style={{
                        width: 10, height: 10, borderRadius: "50%",
                        background: item.color, opacity: 0.8, flexShrink: 0
                    }} />
                    <span style={{ color: "#475569" }}>{item.label}</span>
                </div>
            ))}
            <div style={{ height: 1, background: "#f1f5f9", margin: "6px 0" }} />
            <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 4 }}>
                <div style={{ width: 22, height: 3, background: "#3b82f6", borderRadius: 2 }} />
                <span style={{ color: "#475569" }}>Safest route</span>
            </div>
            <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                <div style={{ width: 22, height: 0, borderTop: "3px dashed #f59e0b" }} />
                <span style={{ color: "#475569" }}>Alternate route</span>
            </div>
        </div>
    )
}
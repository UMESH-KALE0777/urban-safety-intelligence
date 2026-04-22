export default function SafetyLegend() {
    return (
        <div style={{
            position: "absolute", bottom: 24, left: 12,
            background: "white", borderRadius: 10, padding: "10px 14px",
            border: "1px solid #e5e5e5", zIndex: 1000, fontSize: 12
        }}>
            <p style={{ fontWeight: 600, marginBottom: 6, color: "#333" }}>Risk zones</p>
            {[
                { color: "#e8453c", label: "High risk" },
                { color: "#fbbc04", label: "Medium risk" },
                { color: "#34a853", label: "Low risk" },
            ].map(item => (
                <div key={item.label} style={{
                    display: "flex", alignItems: "center",
                    gap: 8, marginBottom: 4
                }}>
                    <div style={{
                        width: 12, height: 12, borderRadius: "50%",
                        background: item.color, opacity: 0.8
                    }} />
                    <span style={{ color: "#555" }}>{item.label}</span>
                </div>
            ))}
            <div style={{ display: "flex", alignItems: "center", gap: 8, marginTop: 4 }}>
                <div style={{ width: 22, height: 3, background: "#1a73e8", borderRadius: 2 }} />
                <span style={{ color: "#555" }}>Safest route</span>
            </div>
            <div style={{ display: "flex", alignItems: "center", gap: 8, marginTop: 4 }}>
                <div style={{
                    width: 22, height: 3, background: "#fbbc04",
                    borderRadius: 2, borderTop: "2px dashed #fbbc04", background: "none",
                    borderBottom: "none", borderLeft: "none", borderRight: "none"
                }} />
                <span style={{ color: "#555" }}>Alternate route</span>
            </div>
        </div>
    )
}
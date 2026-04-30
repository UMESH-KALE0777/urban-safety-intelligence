export default function LoadingSpinner({ message = "Loading..." }) {
    return (
        <div style={{
            position: "absolute", top: "50%", left: "50%",
            transform: "translate(-50%, -50%)", zIndex: 2000,
            background: "white", borderRadius: 16, padding: "20px 28px",
            boxShadow: "0 8px 32px rgba(0,0,0,0.12)", textAlign: "center",
            border: "1px solid #e2e8f0"
        }}>
            <div style={{
                width: 36, height: 36, border: "3px solid #e2e8f0",
                borderTop: "3px solid #3b82f6", borderRadius: "50%",
                animation: "spin 0.8s linear infinite", margin: "0 auto 10px"
            }} />
            <style>{`@keyframes spin { to { transform: rotate(360deg) } }`}</style>
            <p style={{ fontSize: 13, color: "#475569", fontWeight: 500 }}>{message}</p>
        </div>
    )
}
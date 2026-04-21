export default function LoadingSpinner({ message = "Loading..." }) {
    return (
        <div style={{
            textAlign: "center", padding: "12px 16px",
            fontSize: 13, color: "#666", background: "#fff",
            borderBottom: "1px solid #eee"
        }}>
            {message}
        </div>
    )
}


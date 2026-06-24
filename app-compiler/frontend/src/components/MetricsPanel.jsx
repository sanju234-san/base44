export default function MetricsPanel({ result }) {
  if (!result) return null
  const { status, validation, metadata } = result

  const statusConfig = {
    success: { color: "#22c55e", bg: "#052e16", label: "✓ Success" },
    partial_success: { color: "#f59e0b", bg: "#1c1200", label: "⚡ Partial Success" },
    failed: { color: "#ef4444", bg: "#2a0a0a", label: "✗ Failed" },
  }[status] || { color: "#888", bg: "#1a1a1a", label: status }

  return (
    <div className="metrics-panel">
      <div className="metric status-metric" style={{ background: statusConfig.bg, borderColor: statusConfig.color }}>
        <span className="metric-label">Status</span>
        <span className="metric-value" style={{ color: statusConfig.color }}>{statusConfig.label}</span>
      </div>
      <div className="metric">
        <span className="metric-label">Total Latency</span>
        <span className="metric-value">{(metadata?.total_latency_ms / 1000).toFixed(1)}s</span>
      </div>
      <div className="metric">
        <span className="metric-label">Auto Repairs</span>
        <span className="metric-value">
          🔧 {validation?.repairs_successful}/{validation?.repairs_needed}
        </span>
      </div>
      <div className="metric">
        <span className="metric-label">App Type</span>
        <span className="metric-value">{metadata?.app_type}</span>
      </div>
      {validation?.failure_types?.length > 0 && (
        <div className="metric">
          <span className="metric-label">Issues Found</span>
          <div className="failure-tags">
            {validation.failure_types.map((f, i) => (
              <span key={i} className="failure-tag">{f}</span>
            ))}
          </div>
        </div>
      )}
      {metadata?.assumptions?.length > 0 && (
        <div className="assumptions">
          <span className="metric-label">Assumptions made</span>
          <ul>
            {metadata.assumptions.map((a, i) => <li key={i}>{a}</li>)}
          </ul>
        </div>
      )}
    </div>
  )
}
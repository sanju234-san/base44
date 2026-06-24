const STAGE_LABELS = {
  intent: { label: "Stage 1 — Intent Extraction", model: "llama3-8b" },
  design: { label: "Stage 2 — System Design", model: "llama-3.3-70b" },
  schema: { label: "Stage 3 — Schema Generation", model: "llama-3.3-70b" },
  refined: { label: "Stage 4 — Refinement", model: "llama-3.3-70b" },
}

export default function PipelineStatus({ stages }) {
  if (!stages) return null

  return (
    <div className="pipeline-status">
      <h3>Pipeline Stages</h3>
      <div className="stages-grid">
        {Object.entries(stages).map(([key, stage]) => (
          <div key={key} className={`stage-card ${stage?.success ? "success" : "failed"}`}>
            <div className="stage-header">
              <span className="stage-name">{STAGE_LABELS[key]?.label}</span>
              <span className={`stage-badge ${stage?.success ? "green" : "red"}`}>
                {stage?.success ? "✓" : "✗"}
              </span>
            </div>
            <div className="stage-meta">
              <span className="latency">{stage?.latency_ms?.toFixed(0)}ms</span>
              <span className="model-tag">{STAGE_LABELS[key]?.model}</span>
              {stage?.repairs_needed > 0 && (
                <span className="repair-tag">
                  🔧 {stage.repairs_successful}/{stage.repairs_needed} repaired
                </span>
              )}
            </div>
            {stage?.error && <div className="stage-error">{stage.error}</div>}
          </div>
        ))}
      </div>
    </div>
  )
}
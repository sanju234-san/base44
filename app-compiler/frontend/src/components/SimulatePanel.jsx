import { useState } from "react"

export default function SimulatePanel({ schema }) {
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)

  if (!schema) return null

  const handleSimulate = async () => {
    setLoading(true)
    try {
      const res = await fetch("http://127.0.0.1:8000/simulate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ schema })
      })
      const data = await res.json()
      setResult(data)
    } catch (err) {
      setResult({ error: "Simulation failed" })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="simulate-panel">
      <div className="simulate-header">
        <div>
          <h3>Execution Simulation</h3>
          <p>Validates the schema would power a real app</p>
        </div>
        <button className="simulate-btn" onClick={handleSimulate} disabled={loading}>
          {loading ? "Simulating..." : "▶ Run Simulation"}
        </button>
      </div>

      {result && !result.error && (
        <div className="simulate-result">
          <div className={`simulate-verdict ${result.executable ? "pass" : "fail"}`}>
            <span className="verdict-icon">{result.executable ? "✓" : "✗"}</span>
            <span className="verdict-text">{result.verdict}</span>
            <span className="verdict-score">{result.score} checks passed ({result.success_rate}%)</span>
          </div>
          {result.issues?.length > 0 && (
            <div className="simulate-issues">
              {result.issues.map((issue, i) => (
                <div key={i} className="simulate-issue">{issue}</div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
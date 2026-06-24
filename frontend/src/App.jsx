import { useState } from "react"
import PromptInput from "./components/PromptInput"
import PipelineStatus from "./components/PipelineStatus"
import JsonViewer from "./components/JsonViewer"
import MetricsPanel from "./components/MetricsPanel"
import SimulatePanel from "./components/SimulatePanel"
import "./App.css"

function App() {
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [activeTab, setActiveTab] = useState("final")

  const handleGenerate = async (prompt) => {
    setLoading(true)
    setResult(null)
    setError(null)
    setActiveTab("final")

    try {
      const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000"
      const res = await fetch(`${API_URL}/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt })
      })
      const data = await res.json()
      setResult(data)
    } catch (err) {
      setError("Failed to connect to backend. Is the server running?")
    } finally {
      setLoading(false)
    }
  }

  const tabs = [
    { id: "final", label: "Final Schema" },
    { id: "ui", label: "UI Schema" },
    { id: "api", label: "API Schema" },
    { id: "db", label: "DB Schema" },
    { id: "auth", label: "Auth Schema" },
    { id: "stages", label: "Stage Outputs" },
  ]

  const getTabData = () => {
    if (!result?.final_output) return null
    switch (activeTab) {
      case "final": return result.final_output
      case "ui": return result.final_output.ui_schema
      case "api": return result.final_output.api_schema
      case "db": return result.final_output.db_schema
      case "auth": return result.final_output.auth_schema
      case "stages": return result.stages
      default: return result.final_output
    }
  }

  return (
    <div className="app">
      <header>
        <div className="header-inner">
          <h1>⚙️ App Compiler</h1>
          <p>Natural language → validated executable app schema</p>
          <div className="header-badges">
            <span className="badge">4-Stage Pipeline</span>
            <span className="badge">Auto Repair</span>
            <span className="badge">Cross-Layer Validation</span>
          </div>
        </div>
      </header>

      <main>
        <PromptInput onGenerate={handleGenerate} loading={loading} />

        {loading && (
          <div className="pipeline-loading">
            <div className="stages-flow">
              {["Intent Extraction", "System Design", "Schema Generation", "Refinement"].map((s, i) => (
                <div key={i} className="flow-stage">
                  <div className="flow-dot pulsing" />
                  <span>{s}</span>
                  {i < 3 && <div className="flow-arrow">→</div>}
                </div>
              ))}
            </div>
            <p>Running pipeline... ~30-60s</p>
          </div>
        )}

        {error && <div className="error-box">⚠ {error}</div>}

        {result && (
          <>
            <MetricsPanel result={result} />
            <PipelineStatus stages={result.stages} />
            <SimulatePanel schema={result.final_output} />

            {result.final_output && (
              <div className="output-section">
                <div className="tabs">
                  {tabs.map(tab => (
                    <button
                      key={tab.id}
                      className={`tab ${activeTab === tab.id ? "active" : ""}`}
                      onClick={() => setActiveTab(tab.id)}
                    >
                      {tab.label}
                    </button>
                  ))}
                </div>
                <JsonViewer data={getTabData()} title={tabs.find(t => t.id === activeTab)?.label} />
              </div>
            )}
          </>
        )}
      </main>
    </div>
  )
}

export default App
import { useState } from "react"

const EXAMPLES = [
  "Build a CRM with login, contacts, dashboard, role-based access, and premium plan with payments. Admins can see analytics.",
  "Build an e-commerce store with product listings, cart, checkout, payments, and order tracking.",
  "Build a hospital management system with patient records, doctor scheduling, and billing.",
]

export default function PromptInput({ onGenerate, loading }) {
  const [prompt, setPrompt] = useState("")

  return (
    <div className="prompt-box">
      <label className="prompt-label">Describe your app</label>
      <textarea
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        placeholder="e.g. Build a CRM with login, contacts, role-based access, and payments..."
        rows={4}
        disabled={loading}
      />
      <div className="prompt-actions">
        <div className="examples">
          <span className="examples-label">Try:</span>
          {EXAMPLES.map((ex, i) => (
            <button key={i} className="example-btn" onClick={() => setPrompt(ex)} disabled={loading}>
              Example {i + 1}
            </button>
          ))}
        </div>
        <button
          className="generate-btn"
          onClick={() => prompt.trim() && onGenerate(prompt.trim())}
          disabled={loading || !prompt.trim()}
        >
          {loading ? "Compiling..." : "Generate →"}
        </button>
      </div>
    </div>
  )
}
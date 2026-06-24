import { useState } from "react"

export default function JsonViewer({ data, title }) {
  const [copied, setCopied] = useState(false)

  if (!data) return null

  const json = JSON.stringify(data, null, 2)

  const handleCopy = () => {
    navigator.clipboard.writeText(json)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const colorizeJson = (text) => {
    return text
      .replace(/(".*?")\s*:/g, '<span class="json-key">$1</span>:')
      .replace(/:\s*(".*?")/g, ': <span class="json-string">$1</span>')
      .replace(/:\s*(true|false)/g, ': <span class="json-bool">$1</span>')
      .replace(/:\s*(\d+)/g, ': <span class="json-number">$1</span>')
  }

  return (
    <div className="json-viewer">
      <div className="json-header">
        <span className="json-title">{title}</span>
        <div className="json-actions">
          <span className="json-lines">{json.split("\n").length} lines</span>
          <button className="copy-btn" onClick={handleCopy}>
            {copied ? "✓ Copied" : "Copy"}
          </button>
        </div>
      </div>
      <pre
        className="json-content"
        dangerouslySetInnerHTML={{ __html: colorizeJson(json) }}
      />
    </div>
  )
}
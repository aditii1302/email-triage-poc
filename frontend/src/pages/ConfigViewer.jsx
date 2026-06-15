import { useState, useEffect } from "react"

export default function ConfigViewer() {
  const [config, setConfig] = useState(null)

  useEffect(() => {
    fetch("/api/config")
      .then(r => r.json())
      .then(setConfig)
      .catch(() => {})
  }, [])

  if (!config) return <div className="text-gray-400">Loading...</div>

  return (
    <div className="max-w-3xl">
      <h1 className="text-2xl font-bold text-gray-800 mb-6">Config Viewer</h1>
      <div className="space-y-4">
        {Object.entries(config).map(([key, value]) => (
          <div key={key} className="bg-white rounded-lg shadow p-5">
            <h2 className="font-semibold text-gray-700 mb-2">{key}</h2>
            <pre className="text-xs bg-gray-50 p-3 rounded overflow-auto">{typeof value === "string" ? value : JSON.stringify(value, null, 2)}</pre>
          </div>
        ))}
      </div>
    </div>
  )
}

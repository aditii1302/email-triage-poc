import { useState, useEffect } from "react"
import { useParams } from "react-router-dom"

export default function RunDetail() {
  const { id } = useParams()
  const [run, setRun] = useState(null)

  useEffect(() => {
    fetch("/api/runs/" + id)
      .then(r => r.json())
      .then(setRun)
      .catch(() => {})
  }, [id])

  if (!run) return <div className="text-gray-400">Loading...</div>

  return (
    <div className="max-w-4xl">
      <h1 className="text-2xl font-bold text-gray-800 mb-6">Run Detail</h1>
      <div className="space-y-4">
        <div className="bg-white rounded-lg shadow p-5">
          <h2 className="font-semibold text-gray-700 mb-2">Email</h2>
          <p><span className="font-medium">Subject:</span> {run.subject}</p>
          <p><span className="font-medium">From:</span> {run.sender}</p>
          <p><span className="font-medium">Mailbox:</span> {run.mailbox}</p>
        </div>
        {run.stages && run.stages.map(stage => (
          <div key={stage.stage_name} className="bg-white rounded-lg shadow p-5">
            <div className="flex justify-between mb-2">
              <h2 className="font-semibold text-gray-700">{stage.stage_name}</h2>
              <span className={"text-xs px-2 py-1 rounded " + (stage.status === "completed" ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700")}>
                {stage.status}
              </span>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-xs font-medium text-gray-500 mb-1">Input</p>
                <pre className="text-xs bg-gray-50 p-2 rounded overflow-auto max-h-40">{JSON.stringify(stage.input_payload, null, 2)}</pre>
              </div>
              <div>
                <p className="text-xs font-medium text-gray-500 mb-1">Output</p>
                <pre className="text-xs bg-gray-50 p-2 rounded overflow-auto max-h-40">{JSON.stringify(stage.output_payload, null, 2)}</pre>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

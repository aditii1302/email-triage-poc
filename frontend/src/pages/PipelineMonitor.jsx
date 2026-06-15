import { useState, useEffect } from "react"
import { Link } from "react-router-dom"

const STAGES = ["ingest", "intent", "extract", "classify", "dedup", "enrich", "ticket", "route"]

const badgeColor = {
  "Ticket Created": "bg-green-100 text-green-800",
  "Linked Duplicate": "bg-blue-100 text-blue-800",
  "Review": "bg-yellow-100 text-yellow-800",
  "No Action": "bg-gray-100 text-gray-800",
}

export default function PipelineMonitor() {
  const [runs, setRuns] = useState([])

  useEffect(() => {
    const fetchRuns = () => {
      fetch("/api/runs")
        .then(r => r.json())
        .then(setRuns)
        .catch(() => {})
    }
    fetchRuns()
    const interval = setInterval(fetchRuns, 5000)
    return () => clearInterval(interval)
  }, [])

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-800 mb-6">Pipeline Monitor</h1>
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 border-b">
            <tr>
              <th className="text-left px-4 py-3 text-gray-600">Subject</th>
              <th className="text-left px-4 py-3 text-gray-600">Mailbox</th>
              <th className="text-left px-4 py-3 text-gray-600">Stages</th>
              <th className="text-left px-4 py-3 text-gray-600">Outcome</th>
              <th className="text-left px-4 py-3 text-gray-600">Time</th>
              <th className="text-left px-4 py-3 text-gray-600"></th>
            </tr>
          </thead>
          <tbody>
            {runs.length === 0 && (
              <tr><td colSpan={6} className="text-center py-8 text-gray-400">No pipeline runs yet</td></tr>
            )}
            {runs.map(run => (
              <tr key={run.id} className="border-b hover:bg-gray-50">
                <td className="px-4 py-3 font-medium">{run.subject || "(no subject)"}</td>
                <td className="px-4 py-3 text-gray-500">{run.mailbox}</td>
                <td className="px-4 py-3">
                  <div className="flex gap-1">
                    {STAGES.map((s, i) => (
                      <div key={s} title={s} className={"w-6 h-6 rounded text-xs flex items-center justify-center text-white font-bold " + (run.stages_completed >= i + 1 ? "bg-green-500" : "bg-gray-200 text-gray-400")}>
                        {i + 1}
                      </div>
                    ))}
                  </div>
                </td>
                <td className="px-4 py-3">
                  <span className={"px-2 py-1 rounded-full text-xs font-medium " + (badgeColor[run.outcome] || "bg-gray-100 text-gray-600")}>
                    {run.outcome || "Processing"}
                  </span>
                </td>
                <td className="px-4 py-3 text-gray-400 text-xs">{run.created_at}</td>
                <td className="px-4 py-3">
                  <Link to={"/runs/" + run.id} className="text-blue-500 hover:underline text-xs">Details</Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

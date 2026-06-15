import { useState, useEffect } from "react"

export default function ReviewQueue() {
  const [items, setItems] = useState([])

  useEffect(() => {
    fetch("/api/review")
      .then(r => r.json())
      .then(setItems)
      .catch(() => {})
  }, [])

  const resolve = (run_id, action) => {
    fetch("/api/review/" + run_id + "/resolve", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ action })
    })
      .then(r => r.json())
      .then(() => setItems(items.filter(i => i.run_id !== run_id)))
      .catch(() => {})
  }

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-800 mb-6">Review Queue</h1>
      <div className="space-y-4">
        {items.length === 0 && (
          <div className="bg-white rounded-lg shadow p-8 text-center text-gray-400">No items in review queue</div>
        )}
        {items.map(item => (
          <div key={item.run_id} className="bg-white rounded-lg shadow p-5">
            <div className="flex justify-between items-start mb-3">
              <div>
                <p className="font-medium text-gray-800">{item.subject}</p>
                <p className="text-xs text-gray-400 mt-1">{item.mailbox}</p>
              </div>
              <span className="text-xs bg-yellow-100 text-yellow-800 px-2 py-1 rounded">Possible Duplicate</span>
            </div>
            <div className="grid grid-cols-2 gap-4 mb-4">
              <div className="bg-gray-50 rounded p-3">
                <p className="text-xs font-medium text-gray-600 mb-1">New Ticket</p>
                <p className="font-mono text-xs text-blue-700">{item.new_ticket}</p>
                <p className="text-xs text-gray-500 mt-1">{item.problem_statement}</p>
              </div>
              <div className="bg-gray-50 rounded p-3">
                <p className="text-xs font-medium text-gray-600 mb-1">Matched Ticket</p>
                <p className="font-mono text-xs text-purple-700">{item.matched_ticket}</p>
              </div>
            </div>
            <div className="flex gap-3">
              <button onClick={() => resolve(item.run_id, "merge")} className="bg-red-500 text-white px-4 py-2 rounded text-sm hover:bg-red-600">
                Confirm Duplicate (merge & close)
              </button>
              <button onClick={() => resolve(item.run_id, "keep")} className="bg-green-500 text-white px-4 py-2 rounded text-sm hover:bg-green-600">
                Not a Duplicate (keep both)
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

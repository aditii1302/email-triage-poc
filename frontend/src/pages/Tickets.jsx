import { useState, useEffect } from "react"

export default function Tickets() {
  const [tickets, setTickets] = useState([])

  useEffect(() => {
    const fetchTickets = () => {
      fetch("/api/tickets")
        .then(r => r.json())
        .then(setTickets)
        .catch(() => {})
    }
    fetchTickets()
    const interval = setInterval(fetchTickets, 15000)
    return () => clearInterval(interval)
  }, [])

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-800 mb-6">Tickets</h1>
      <div className="space-y-4">
        {tickets.length === 0 && (
          <div className="bg-white rounded-lg shadow p-8 text-center text-gray-400">No tickets yet</div>
        )}
        {tickets.map(ticket => (
          <div key={ticket.itsm_a_id} className="bg-white rounded-lg shadow p-5">
            <div className="flex justify-between items-start mb-3">
              <div>
                <span className="font-mono text-xs bg-blue-50 text-blue-700 px-2 py-1 rounded mr-2">{ticket.itsm_a_number}</span>
                <span className="font-mono text-xs bg-purple-50 text-purple-700 px-2 py-1 rounded">{ticket.itsm_b_key}</span>
              </div>
              <span className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded">{ticket.priority}</span>
            </div>
            <p className="font-medium text-gray-800 mb-2">{ticket.short_description}</p>
            <div className="grid grid-cols-2 gap-2 text-xs text-gray-500">
              <div><span className="font-medium">Category:</span> {ticket.category}</div>
              <div><span className="font-medium">Application:</span> {ticket.ai_impacted_application}</div>
              <div><span className="font-medium">Business Unit:</span> {ticket.ai_impacted_business_unit}</div>
              <div><span className="font-medium">Dedup Status:</span> {ticket.ai_duplicate_check_status}</div>
              <div><span className="font-medium">Intent Confidence:</span> {ticket.ai_intent_confidence}</div>
              <div><span className="font-medium">Caller:</span> {ticket.caller}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

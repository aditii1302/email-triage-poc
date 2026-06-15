import { useState } from "react"

export default function MailSimulator() {
  const [form, setForm] = useState({
    mailbox: "inbox_1",
    from_addr: "user@example.com",
    to_addr: "support@example.com",
    subject: "",
    body: ""
  })
  const [status, setStatus] = useState(null)

  const handleSubmit = () => {
    setStatus("sending")
    fetch("/api/simulate/email", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(form)
    })
      .then(r => r.json())
      .then(() => setStatus("sent"))
      .catch(() => setStatus("error"))
  }

  return (
    <div className="max-w-2xl">
      <h1 className="text-2xl font-bold text-gray-800 mb-6">Mail Simulator</h1>
      <div className="bg-white rounded-lg shadow p-6 space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Mailbox</label>
          <select className="w-full border rounded px-3 py-2 text-sm" value={form.mailbox} onChange={e => setForm({...form, mailbox: e.target.value})}>
            <option value="inbox_1">Inbox 1</option>
            <option value="inbox_2">Inbox 2</option>
            <option value="inbox_3">Inbox 3</option>
            <option value="inbox_4">Inbox 4</option>
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">From</label>
          <input className="w-full border rounded px-3 py-2 text-sm" value={form.from_addr} onChange={e => setForm({...form, from_addr: e.target.value})} />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">To</label>
          <input className="w-full border rounded px-3 py-2 text-sm" value={form.to_addr} onChange={e => setForm({...form, to_addr: e.target.value})} />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Subject</label>
          <input className="w-full border rounded px-3 py-2 text-sm" value={form.subject} onChange={e => setForm({...form, subject: e.target.value})} />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Body</label>
          <textarea className="w-full border rounded px-3 py-2 text-sm h-32" value={form.body} onChange={e => setForm({...form, body: e.target.value})} />
        </div>
        <button onClick={handleSubmit} className="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700 text-sm font-medium">
          Send Email
        </button>
        {status === "sent" && <p className="text-green-600 text-sm">Email injected successfully! Check the Pipeline Monitor.</p>}
        {status === "error" && <p className="text-red-600 text-sm">Failed to send. Is the backend running?</p>}
      </div>
    </div>
  )
}

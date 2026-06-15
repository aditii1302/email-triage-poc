import { BrowserRouter, Routes, Route, NavLink } from "react-router-dom"
import PipelineMonitor from "./pages/PipelineMonitor"
import MailSimulator from "./pages/MailSimulator"
import Tickets from "./pages/Tickets"
import ReviewQueue from "./pages/ReviewQueue"
import RunDetail from "./pages/RunDetail"
import ConfigViewer from "./pages/ConfigViewer"

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-50">
        <nav className="bg-white border-b border-gray-200 px-6 py-3 flex gap-6 shadow-sm">
          <span className="font-bold text-gray-800 mr-4">Email Triage POC</span>
          <NavLink to="/" end className={({isActive}) => isActive ? "text-blue-600 font-medium" : "text-gray-500 hover:text-gray-800"}>Monitor</NavLink>
          <NavLink to="/simulate" className={({isActive}) => isActive ? "text-blue-600 font-medium" : "text-gray-500 hover:text-gray-800"}>Mail Simulator</NavLink>
          <NavLink to="/tickets" className={({isActive}) => isActive ? "text-blue-600 font-medium" : "text-gray-500 hover:text-gray-800"}>Tickets</NavLink>
          <NavLink to="/review" className={({isActive}) => isActive ? "text-blue-600 font-medium" : "text-gray-500 hover:text-gray-800"}>Review Queue</NavLink>
          <NavLink to="/config" className={({isActive}) => isActive ? "text-blue-600 font-medium" : "text-gray-500 hover:text-gray-800"}>Config</NavLink>
        </nav>
        <main className="p-6">
          <Routes>
            <Route path="/" element={<PipelineMonitor />} />
            <Route path="/simulate" element={<MailSimulator />} />
            <Route path="/tickets" element={<Tickets />} />
            <Route path="/review" element={<ReviewQueue />} />
            <Route path="/runs/:id" element={<RunDetail />} />
            <Route path="/config" element={<ConfigViewer />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}

export default App

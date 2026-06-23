import { useState, useEffect } from 'react'
import { io } from 'socket.io-client'
import axios from 'axios'

function App() {
  const [status, setStatus] = useState("Checking backend...")

  useEffect(() => {
    // Basic test to see if backend is reachable
    axios.get("http://localhost:8000/")
      .then(res => setStatus(res.data.message))
      .catch(err => setStatus("Backend is unreachable"))
  }, [])

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col items-center justify-center p-4">
      <div className="bg-white p-8 rounded-xl shadow-lg max-w-lg w-full text-center border border-gray-100">
        <h1 className="text-3xl font-extrabold text-indigo-600 mb-4 tracking-tight">Multi-Agent SaaS Dashboard</h1>
        <p className="text-gray-500 mb-8">Your intelligent agents are ready to work for you.</p>
        
        <div className="p-5 bg-indigo-50 rounded-lg border border-indigo-100 mb-8">
          <h2 className="text-xs font-bold text-indigo-400 uppercase tracking-wider mb-2">Backend API Status</h2>
          <div className="flex items-center justify-center gap-2">
            <span className={`w-3 h-3 rounded-full ${status.includes('unreachable') ? 'bg-red-500' : 'bg-green-500 animate-pulse'}`}></span>
            <p className="text-lg font-medium text-indigo-900">{status}</p>
          </div>
        </div>
        
        <div className="grid grid-cols-2 gap-4">
          <button className="bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-3 px-4 rounded-lg shadow-sm transition-all duration-200">
            View Agents
          </button>
          <button className="bg-white hover:bg-gray-50 text-gray-700 font-semibold py-3 px-4 border border-gray-200 rounded-lg shadow-sm transition-all duration-200">
            Settings
          </button>
        </div>
      </div>
    </div>
  )
}

export default App

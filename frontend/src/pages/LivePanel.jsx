import { useState, useEffect, useRef } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { Loader2, CheckCircle2, Clock, Terminal } from "lucide-react";
import io from "socket.io-client";
import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export default function LivePanel() {
  const location = useLocation();
  const navigate = useNavigate();
  const { task, formatPref } = location.state || {};

  const [logs, setLogs] = useState([]);
  const [agents, setAgents] = useState({
    "Research Agent": "waiting", // waiting, running, completed, error
    "Writer Agent": "waiting",
    "Reviewer Agent": "waiting"
  });
  
  const logsEndRef = useRef(null);

  useEffect(() => {
    if (!task) {
      navigate("/");
      return;
    }

    // Connect to WebSocket
    // Note: The backend uses standard WebSocket, not socket.io
    const wsUrl = API_URL.replace(/^http/, "ws") + "/ws/status";
    const ws = new WebSocket(wsUrl);
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setLogs((prev) => [...prev, data]);

      if (data.agent && agents[data.agent] !== undefined) {
        if (data.status === "started") {
          setAgents((prev) => ({ ...prev, [data.agent]: "running" }));
        } else if (data.status === "completed") {
          setAgents((prev) => ({ ...prev, [data.agent]: "completed" }));
        } else if (data.status === "error") {
          setAgents((prev) => ({ ...prev, [data.agent]: "error" }));
        }
      }
    };

    ws.onopen = () => {
      // Trigger the backend task execution after WS connects
      axios.post(`${API_URL}/run-task`, {
        task,
        format_pref: formatPref
      }, {
        headers: { "X-API-Key": "default-dev-key" }
      })
      .then((res) => {
        // The backend returns when the entire pipeline finishes
        setTimeout(() => {
          navigate(`/result/${res.data.task_id}`);
        }, 1500); // Small delay to let the user see the final green checks
      })
      .catch((err) => {
        setLogs((prev) => [...prev, { agent: "System", status: "error", message: `Failed to execute task: ${err.message}`, timestamp: new Date().toISOString() }]);
      });
    };

    return () => {
      ws.close();
    };
  }, [task, formatPref, navigate]);

  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [logs]);

  // Calculate progress
  const completedCount = Object.values(agents).filter(s => s === "completed").length;
  const runningCount = Object.values(agents).filter(s => s === "running").length;
  const progress = (completedCount * 33.3) + (runningCount * 16.5); // approximate progress

  const AgentCard = ({ name, status, delay }) => {
    const isRunning = status === "running";
    const isCompleted = status === "completed";
    const isError = status === "error";

    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay }}
        className={`glass-panel p-6 relative overflow-hidden transition-all duration-500 ${
          isRunning ? "border-blue-500/50 shadow-[0_0_30px_-5px_rgba(59,130,246,0.3)]" : 
          isCompleted ? "border-green-500/50" : 
          isError ? "border-red-500/50" : "opacity-70"
        }`}
      >
        <div className="flex items-center justify-between mb-4 relative z-10">
          <h3 className="font-semibold text-lg">{name}</h3>
          {isRunning && <Loader2 className="animate-spin text-blue-500" />}
          {isCompleted && <CheckCircle2 className="text-green-500" />}
          {status === "waiting" && <Clock className="text-zinc-500" />}
        </div>
        
        <div className="text-sm text-zinc-400 relative z-10">
          {isRunning && "Working on it..."}
          {isCompleted && "Task finished"}
          {status === "waiting" && "Waiting in queue"}
          {isError && "Failed"}
        </div>

        {/* Animated background glow for running state */}
        {isRunning && (
          <div className="absolute inset-0 bg-blue-500/10 animate-pulse pointer-events-none" />
        )}
      </motion.div>
    );
  };

  return (
    <div className="max-w-5xl mx-auto space-y-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Processing Task</h1>
        <p className="text-zinc-400">"{task}"</p>
      </div>

      {/* Progress Bar */}
      <div className="w-full bg-zinc-900 rounded-full h-2.5 mb-8 overflow-hidden">
        <motion.div 
          className="bg-blue-600 h-2.5 rounded-full"
          initial={{ width: 0 }}
          animate={{ width: `${Math.min(progress, 100)}%` }}
          transition={{ duration: 0.5 }}
        />
      </div>

      {/* Agent Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <AgentCard name="Research Agent" status={agents["Research Agent"]} delay={0.1} />
        <AgentCard name="Writer Agent" status={agents["Writer Agent"]} delay={0.2} />
        <AgentCard name="Reviewer Agent" status={agents["Reviewer Agent"]} delay={0.3} />
      </div>

      {/* Terminal Logs */}
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="glass-panel p-4 mt-8 flex flex-col h-80"
      >
        <div className="flex items-center text-zinc-400 mb-4 pb-4 border-b border-zinc-800">
          <Terminal size={18} className="mr-2" />
          <span className="text-sm font-medium tracking-wider uppercase">Live Activity Log</span>
        </div>
        <div className="flex-1 overflow-y-auto space-y-3 font-mono text-sm pr-2">
          {logs.map((log, i) => (
            <motion.div 
              key={i} 
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              className="flex items-start"
            >
              <span className="text-zinc-500 mr-4 shrink-0">
                {new Date(log.timestamp || Date.now()).toLocaleTimeString()}
              </span>
              <span className={`font-semibold mr-2 ${
                log.agent === 'Orchestrator' ? 'text-purple-400' :
                log.agent === 'Research Agent' ? 'text-blue-400' :
                log.agent === 'Writer Agent' ? 'text-emerald-400' :
                'text-amber-400'
              }`}>
                [{log.agent}]
              </span>
              <span className="text-zinc-300 break-words">{log.message}</span>
            </motion.div>
          ))}
          <div ref={logsEndRef} />
        </div>
      </motion.div>
    </div>
  );
}

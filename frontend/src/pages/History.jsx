import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { Trash2, ExternalLink, Search, Filter } from "lucide-react";
import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export default function History() {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filterFormat, setFilterFormat] = useState("all");
  const [searchQuery, setSearchQuery] = useState("");

  useEffect(() => {
    fetchTasks();
  }, []);

  const fetchTasks = () => {
    setLoading(true);
    fetch(`${API_URL}/tasks`, {
      headers: { "X-API-Key": "default-dev-key" }
    })
    .then(async res => {
      if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
      const data = await res.json();
      setTasks(data);
      setLoading(false);
    })
    .catch(err => {
      console.error(err);
      setLoading(false);
    });
  };

  const handleDelete = async (e, id) => {
    e.preventDefault();
    e.stopPropagation();
    
    if (!window.confirm("Are you sure you want to delete this task?")) return;
    
    try {
      const res = await fetch(`${API_URL}/task/${id}`, {
        method: 'DELETE',
        headers: { "X-API-Key": "default-dev-key" }
      });
      if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
      setTasks(tasks.filter(t => t.task_id !== id));
    } catch (err) {
      console.error("Failed to delete", err);
      alert("Failed to delete task");
    }
  };

  const filteredTasks = tasks.filter(task => {
    const matchesFormat = filterFormat === "all" || task.format_pref === filterFormat;
    const matchesSearch = task.task.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesFormat && matchesSearch;
  });

  return (
    <motion.div 
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="max-w-6xl mx-auto"
    >
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold">Task History</h1>
          <p className="text-zinc-400 mt-2">View and manage your previously generated content.</p>
        </div>
      </div>

      <div className="glass-panel p-6 mb-8 flex flex-col md:flex-row gap-4 justify-between items-center">
        <div className="relative w-full md:w-96">
          <Search className="absolute left-3 top-3 text-zinc-500" size={18} />
          <input 
            type="text"
            placeholder="Search by topic..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-zinc-950/50 border border-zinc-800 rounded-lg pl-10 pr-4 py-2.5 text-sm text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div className="flex items-center space-x-2 w-full md:w-auto">
          <Filter size={18} className="text-zinc-500" />
          <select 
            value={filterFormat}
            onChange={(e) => setFilterFormat(e.target.value)}
            className="bg-zinc-950/50 border border-zinc-800 rounded-lg px-4 py-2.5 text-sm text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">All Formats</option>
            <option value="blog">Blog Post</option>
            <option value="report">Report</option>
            <option value="email">Email</option>
            <option value="social">Social Post</option>
          </select>
        </div>
      </div>

      <div className="glass-panel overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-zinc-900/50 border-b border-zinc-800 text-sm font-semibold text-zinc-400">
                <th className="p-4">Topic</th>
                <th className="p-4">Format</th>
                <th className="p-4">Score</th>
                <th className="p-4">Date</th>
                <th className="p-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-zinc-800/50">
              {loading ? (
                <tr>
                  <td colSpan="5" className="p-8 text-center text-zinc-500">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto mb-4"></div>
                    Loading history...
                  </td>
                </tr>
              ) : filteredTasks.length === 0 ? (
                <tr>
                  <td colSpan="5" className="p-8 text-center text-zinc-500">
                    No tasks found.
                  </td>
                </tr>
              ) : (
                filteredTasks.map((task) => (
                  <tr key={task.task_id} className="hover:bg-zinc-800/30 transition-colors group">
                    <td className="p-4">
                      <div className="font-medium text-zinc-200 line-clamp-1">{task.task}</div>
                      <div className="text-xs text-zinc-500 mt-1">ID: {task.task_id.substring(0, 8)}...</div>
                    </td>
                    <td className="p-4">
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-500/10 text-blue-400 capitalize border border-blue-500/20">
                        {task.format_pref}
                      </span>
                    </td>
                    <td className="p-4">
                      <div className={`font-semibold ${
                        (task.score || 0) >= 8 ? 'text-green-500' : 
                        (task.score || 0) >= 5 ? 'text-yellow-500' : 'text-red-500'
                      }`}>
                        {task.score || 0}/10
                      </div>
                    </td>
                    <td className="p-4 text-sm text-zinc-400">
                      {new Date(task.created_at).toLocaleDateString()}
                    </td>
                    <td className="p-4 text-right space-x-2">
                      <Link 
                        to={`/result/${task.task_id}`}
                        className="inline-flex p-2 text-zinc-400 hover:text-blue-400 hover:bg-blue-400/10 rounded-lg transition-colors"
                        title="View Result"
                      >
                        <ExternalLink size={18} />
                      </Link>
                      <button 
                        onClick={(e) => handleDelete(e, task.task_id)}
                        className="inline-flex p-2 text-zinc-400 hover:text-red-400 hover:bg-red-400/10 rounded-lg transition-colors"
                        title="Delete Task"
                      >
                        <Trash2 size={18} />
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </motion.div>
  );
}

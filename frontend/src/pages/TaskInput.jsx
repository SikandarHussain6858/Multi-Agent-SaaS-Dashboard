import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { Send, FileText, ChevronDown } from "lucide-react";

export default function TaskInput() {
  const [task, setTask] = useState("");
  const [formatPref, setFormatPref] = useState("blog");
  const navigate = useNavigate();

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!task.trim()) return;
    
    navigate("/live", { state: { task, formatPref } });
  };

  const formats = [
    { id: "blog", label: "Blog Post" },
    { id: "report", label: "Report" },
    { id: "email", label: "Email" },
    { id: "social", label: "Social Post" },
  ];

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="max-w-3xl mx-auto mt-12"
    >
      <div className="text-center mb-12">
        <h1 className="text-4xl font-extrabold mb-4 tracking-tight">What would you like to create?</h1>
        <p className="text-zinc-400 text-lg">Enter a topic and let our multi-agent pipeline generate high-quality content for you.</p>
      </div>

      <form onSubmit={handleSubmit} className="glass-panel p-8 shadow-2xl shadow-blue-900/20">
        <div className="mb-6">
          <label className="block text-sm font-medium text-zinc-300 mb-2">Topic or Instructions</label>
          <textarea
            value={task}
            onChange={(e) => setTask(e.target.value)}
            placeholder="e.g. Write a comprehensive guide on the future of quantum computing..."
            className="w-full h-40 bg-zinc-950/50 border border-zinc-700 rounded-xl p-4 text-white placeholder:text-zinc-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none transition-all"
          />
        </div>

        <div className="mb-8">
          <label className="block text-sm font-medium text-zinc-300 mb-2">Output Format</label>
          <div className="relative">
            <select
              value={formatPref}
              onChange={(e) => setFormatPref(e.target.value)}
              className="w-full appearance-none bg-zinc-950/50 border border-zinc-700 rounded-xl p-4 text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
            >
              {formats.map((f) => (
                <option key={f.id} value={f.id} className="bg-zinc-900">
                  {f.label}
                </option>
              ))}
            </select>
            <ChevronDown className="absolute right-4 top-4 text-zinc-400 pointer-events-none" size={20} />
          </div>
        </div>

        <button
          type="submit"
          disabled={!task.trim()}
          className="w-full flex items-center justify-center py-4 px-6 rounded-xl bg-blue-600 hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold text-lg transition-all transform hover:scale-[1.02] active:scale-[0.98] shadow-lg shadow-blue-600/30"
        >
          <Send className="mr-2" size={20} />
          Generate Content
        </button>
      </form>
    </motion.div>
  );
}

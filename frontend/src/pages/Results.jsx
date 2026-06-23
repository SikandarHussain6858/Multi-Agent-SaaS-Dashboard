import { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import { motion } from "framer-motion";
import { Copy, Download, CheckCircle2, AlertTriangle, ArrowLeft } from "lucide-react";
import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export default function Results() {
  const { id } = useParams();
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(true);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    fetch(`${API_URL}/task/${id}`, {
      headers: { "X-API-Key": "default-dev-key" }
    })
    .then(async res => {
      if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
      const data = await res.json();
      setResult(data);
      setLoading(false);
    })
    .catch(err => {
      console.error(err);
      setLoading(false);
    });
  }, [id]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (!result) {
    return (
      <div className="text-center mt-20">
        <h2 className="text-2xl font-bold mb-4">Task Not Found</h2>
        <Link to="/" className="text-blue-500 hover:underline">Go back home</Link>
      </div>
    );
  }

  const handleCopy = () => {
    navigator.clipboard.writeText(result.output || "");
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    const element = document.createElement("a");
    const file = new Blob([result.output || ""], {type: 'text/plain'});
    element.href = URL.createObjectURL(file);
    element.download = `task_${id.substring(0, 8)}.txt`;
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  // Parse feedback if it's stringified JSON
  let feedbackText = result.feedback;
  try {
    const parsed = JSON.parse(result.feedback);
    feedbackText = parsed.feedback || result.feedback;
  } catch (e) {
    // leave as is
  }

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="max-w-4xl mx-auto space-y-8"
    >
      <div className="flex items-center justify-between mb-8">
        <div>
          <Link to="/" className="inline-flex items-center text-sm text-zinc-400 hover:text-white mb-4 transition-colors">
            <ArrowLeft size={16} className="mr-1" /> Back to Dashboard
          </Link>
          <h1 className="text-3xl font-bold">Generated Content</h1>
          <p className="text-zinc-400 mt-2">Topic: {result.task}</p>
        </div>

        <div className="flex flex-col items-end">
          <div className="text-sm text-zinc-400 mb-1">Quality Score</div>
          <div className={`text-3xl font-bold ${
            (result.score || 0) >= 8 ? 'text-green-500' : 
            (result.score || 0) >= 5 ? 'text-yellow-500' : 'text-red-500'
          }`}>
            {result.score || 0}/10
          </div>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-6">
        <div className="col-span-2 glass-panel p-6">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-xl font-semibold">Final Output</h2>
            <div className="flex space-x-2">
              <button 
                onClick={handleCopy}
                className="p-2 bg-zinc-800 hover:bg-zinc-700 rounded-lg text-zinc-300 transition-colors flex items-center"
                title="Copy to clipboard"
              >
                {copied ? <CheckCircle2 size={18} className="text-green-500" /> : <Copy size={18} />}
              </button>
              <button 
                onClick={handleDownload}
                className="p-2 bg-zinc-800 hover:bg-zinc-700 rounded-lg text-zinc-300 transition-colors flex items-center"
                title="Download TXT"
              >
                <Download size={18} />
              </button>
            </div>
          </div>
          
          <div className="prose prose-invert max-w-none">
            <div className="whitespace-pre-wrap font-serif text-zinc-300 leading-relaxed">
              {result.output || "No output generated."}
            </div>
          </div>
        </div>

        <div className="col-span-1 space-y-6">
          <div className="glass-panel p-6">
            <div className="flex items-center mb-4">
              <AlertTriangle className="text-yellow-500 mr-2" size={20} />
              <h2 className="text-lg font-semibold">Reviewer Feedback</h2>
            </div>
            <div className="text-zinc-400 text-sm whitespace-pre-wrap">
              {feedbackText || "No feedback provided."}
            </div>
          </div>

          <div className="glass-panel p-6">
            <h2 className="text-lg font-semibold mb-4">Metadata</h2>
            <div className="space-y-3 text-sm">
              <div className="flex justify-between border-b border-zinc-800 pb-2">
                <span className="text-zinc-500">Format</span>
                <span className="capitalize">{result.format_pref}</span>
              </div>
              <div className="flex justify-between border-b border-zinc-800 pb-2">
                <span className="text-zinc-500">Status</span>
                <span className="capitalize text-green-500">{result.status}</span>
              </div>
              <div className="flex justify-between border-b border-zinc-800 pb-2">
                <span className="text-zinc-500">Created</span>
                <span>{new Date(result.created_at).toLocaleDateString()}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
}

import { Link, Outlet, useLocation } from "react-router-dom";
import { LayoutDashboard, History, Sparkles, Settings } from "lucide-react";
import { cn } from "../lib/utils.js";

export default function Layout() {
  const location = useLocation();

  const navItems = [
    { name: "New Task", path: "/", icon: <LayoutDashboard size={20} /> },
    { name: "Task History", path: "/history", icon: <History size={20} /> },
  ];

  return (
    <div className="flex h-screen bg-[#09090b] text-white overflow-hidden">
      {/* Sidebar */}
      <aside className="w-64 border-r border-zinc-800 bg-[#09090b] flex flex-col">
        <div className="h-16 flex items-center px-6 border-b border-zinc-800">
          <Sparkles className="text-blue-500 mr-2" size={24} />
          <h1 className="text-xl font-bold gradient-text tracking-tight">Antigravity AI</h1>
        </div>
        
        <nav className="flex-1 px-4 py-6 space-y-2">
          {navItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={cn(
                "flex items-center px-4 py-3 rounded-lg text-sm font-medium transition-all duration-200",
                location.pathname === item.path
                  ? "bg-blue-600/10 text-blue-500 border border-blue-500/20"
                  : "text-zinc-400 hover:text-white hover:bg-zinc-800/50"
              )}
            >
              <span className="mr-3">{item.icon}</span>
              {item.name}
            </Link>
          ))}
        </nav>

        <div className="p-4 border-t border-zinc-800">
          <button className="flex items-center w-full px-4 py-3 text-sm font-medium text-zinc-400 hover:text-white hover:bg-zinc-800/50 rounded-lg transition-colors">
            <Settings size={20} className="mr-3" />
            Settings
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto relative">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-blue-900/20 via-[#09090b] to-[#09090b] pointer-events-none" />
        <div className="relative z-10 h-full p-8 max-w-6xl mx-auto">
          <Outlet />
        </div>
      </main>
    </div>
  );
}

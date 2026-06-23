import { Routes, Route } from "react-router-dom";
import Layout from "./components/AppLayout.jsx";
import TaskInput from "./pages/TaskInput.jsx";
import LivePanel from "./pages/LivePanel.jsx";
import Results from "./pages/Results.jsx";
import History from "./pages/History.jsx";

function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<TaskInput />} />
        <Route path="live" element={<LivePanel />} />
        <Route path="result/:id" element={<Results />} />
        <Route path="history" element={<History />} />
      </Route>
    </Routes>
  );
}

export default App;

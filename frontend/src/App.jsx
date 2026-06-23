import { Routes, Route } from "react-router-dom";
import Layout from "./components/Layout";
import TaskInput from "./pages/TaskInput";
import LivePanel from "./pages/LivePanel";
import Results from "./pages/Results";
import History from "./pages/History";

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

import { useState, useEffect } from "react";
import ChatPage from "./pages/ChatPage";

function App() {
  const [apiStatus, setApiStatus] = useState("checking");

  useEffect(() => {
    fetch("/api/health")
      .then((res) => res.json())
      .then((data) => setApiStatus(data.status === "healthy" ? "ok" : "error"))
      .catch(() => setApiStatus("error"));
  }, []);

  return (
    <div className="h-screen flex">
      <ChatPage apiStatus={apiStatus} />
    </div>
  );
}

export default App;

import { useState, useEffect } from "react";
import Sidebar from "../components/Sidebar";
import ChatWindow from "../components/ChatWindow";
import ChatInput from "../components/ChatInput";
import useChat from "../hooks/useChat";
import { Icons } from "../utils/Icons";

export default function ChatPage({ apiStatus }) {
  const {
    messages,
    isLoading,
    sessionId,
    agent,
    streamingContent,
    statusMessage,
    isConnected,
    setAgent,
    sendChat,
    loadSession,
    newChat,
  } = useChat();

  const [sessions, setSessions] = useState([]);
  const [sidebarOpen, setSidebarOpen] = useState(true);

  useEffect(() => {
    fetchSessions();
  }, [sessionId]);

  const fetchSessions = async () => {
    try {
      const res = await fetch("/api/sessions");
      const data = await res.json();
      setSessions(data.sessions || []);
    } catch (err) {
      console.error("Failed to fetch sessions");
    }
  };

  const deleteSession = async (id) => {
    try {
      await fetch(`/api/sessions/${id}`, { method: "DELETE" });
      setSessions((prev) => prev.filter((s) => s.id !== id));
      if (sessionId === id) newChat();
    } catch (err) {}
  };

  return (
    <div className="flex w-full h-full overflow-hidden">
      {sidebarOpen && (
        <Sidebar
          sessions={sessions}
          activeSessionId={sessionId}
          activeAgent={agent}
          onSelectSession={loadSession}
          onNewChat={newChat}
          onDeleteSession={deleteSession}
          onAgentChange={setAgent}
          onClose={() => setSidebarOpen(false)}
          isConnected={isConnected}
        />
      )}

      <div className="flex-1 flex flex-col min-w-0 h-full">
        {/* Sleek Top Navbar */}
        <div className="flex items-center justify-between h-16 px-6">
          <div className="flex items-center">
            {!sidebarOpen && (
              <button
                onClick={() => setSidebarOpen(true)}
                className="p-2 rounded-full hover:bg-bg-secondary text-text-secondary mr-4 transition-colors"
              >
                <Icons.Menu />
              </button>
            )}
            <AgentBadge agent={agent} />
          </div>
        </div>

        {/* Scrolling Chat Area */}
        <div className="flex-1 overflow-y-auto w-full">
          <ChatWindow
            messages={messages}
            isLoading={isLoading}
            streamingContent={streamingContent}
            statusMessage={statusMessage}
            agent={agent}
          />
        </div>

        {/* Input Docked to Bottom */}
        <div className="pt-2 pb-6 w-full bg-linear-to-t from-bg-primary via-bg-primary to-transparent z-10">
          <ChatInput onSend={sendChat} isLoading={isLoading} agent={agent} />
        </div>
      </div>
    </div>
  );
}

function AgentBadge({ agent }) {
  const getAgentDetails = () => {
    switch (agent) {
      case "health":
        return { name: "Health Model", icon: <Icons.Health /> };
      case "sports":
        return { name: "Sports Model", icon: <Icons.Sports /> };
      case "education":
        return { name: "Education Model", icon: <Icons.Education /> };
      default:
        return { name: "AI Model", icon: <Icons.AI /> };
    }
  };

  const details = getAgentDetails();

  return (
    <div className="flex items-center gap-2.5 px-3 py-1.5 rounded-lg bg-bg-secondary border border-border-primary cursor-pointer hover:bg-bg-hover transition-colors">
      <div className="text-text-secondary">{details.icon}</div>
      <span className="text-sm font-medium text-text-primary">
        {details.name}
      </span>
      <svg
        width="14"
        height="14"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        className="text-text-tertiary ml-1"
      >
        <path d="m6 9 6 6 6-6" />
      </svg>
    </div>
  );
}

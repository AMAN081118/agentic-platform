import { useState } from "react";
import { Icons } from "../utils/Icons";

const AGENTS = [
  {
    id: "health",
    name: "Health Assistant",
    icon: Icons.Health,
    desc: "Wellness & medical info",
  },
  {
    id: "sports",
    name: "Sports Analyst",
    icon: Icons.Sports,
    desc: "Fitness & sports",
  },
  {
    id: "education",
    name: "Education Tutor",
    icon: Icons.Education,
    desc: "Learning & study help",
  },
];

export default function Sidebar({
  sessions,
  activeSessionId,
  activeAgent,
  onSelectSession,
  onNewChat,
  onDeleteSession,
  onAgentChange,
  onClose,
  isConnected,
}) {
  const [hoveredSession, setHoveredSession] = useState(null);

  const today = new Date().toDateString();
  const yesterday = new Date(Date.now() - 86400000).toDateString();

  const grouped = { today: [], yesterday: [], older: [] };

  sessions.forEach((s) => {
    const date = new Date(s.created_at).toDateString();
    if (date === today) grouped.today.push(s);
    else if (date === yesterday) grouped.yesterday.push(s);
    else grouped.older.push(s);
  });

  return (
    <div className="w-72 h-full bg-bg-secondary flex flex-col ">
      {/* Header */}
      <div className="flex items-center justify-between p-4 h-16">
        <button
          onClick={onClose}
          className="p-2 rounded-full hover:bg-bg-hover text-text-secondary transition-colors"
        >
          <Icons.Menu />
        </button>
        <button
          onClick={onNewChat}
          className="p-2 rounded-full hover:bg-bg-hover text-text-secondary transition-colors"
          title="New chat"
        >
          <Icons.Edit />
        </button>
      </div>

      {/* Agent Selector */}
      <div className="px-3 pb-4">
        <p className="text-xs font-semibold text-text-tertiary mb-3 px-2">
          Workspaces
        </p>
        <div className="space-y-1">
          {AGENTS.map((a) => {
            const Icon = a.icon;
            return (
              <button
                key={a.id}
                onClick={() => onAgentChange(a.id)}
                className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-left transition-all ${
                  activeAgent === a.id
                    ? "bg-bg-active text-text-primary shadow-sm"
                    : "text-text-secondary hover:bg-bg-hover hover:text-text-primary"
                }`}
              >
                <div
                  className={`p-1.5 rounded-lg ${activeAgent === a.id ? "bg-bg-hover text-accent" : ""}`}
                >
                  <Icon />
                </div>
                <div className="min-w-0">
                  <div className="text-sm font-medium truncate">{a.name}</div>
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Chat History */}
      <div className="flex-1 overflow-y-auto px-3">
        <p className="text-xs font-semibold text-text-tertiary mb-3 px-2 mt-2">
          Recent
        </p>
        {sessions.length === 0 ? (
          <p className="text-sm text-text-tertiary text-center py-8">
            No conversations
          </p>
        ) : (
          <div className="space-y-4">
            {grouped.today.length > 0 && (
              <SessionGroup
                label="Today"
                sessions={grouped.today}
                {...groupProps()}
              />
            )}
            {grouped.yesterday.length > 0 && (
              <SessionGroup
                label="Yesterday"
                sessions={grouped.yesterday}
                {...groupProps()}
              />
            )}
            {grouped.older.length > 0 && (
              <SessionGroup
                label="Previous"
                sessions={grouped.older}
                {...groupProps()}
              />
            )}
          </div>
        )}
      </div>

      {/* Footer System Status */}
      <div className="p-4 border-t border-border-primary bg-bg-secondary">
        <div className="flex items-center gap-2.5 px-2">
          <div className="relative flex h-2 w-2">
            {isConnected && (
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            )}
            <span
              className={`relative inline-flex rounded-full h-2 w-2 ${isConnected ? "bg-emerald-500" : "bg-yellow-500"}`}
            ></span>
          </div>
          <span className="text-xs font-medium text-text-secondary">
            {isConnected ? "System Online" : "REST API Fallback"}
          </span>
        </div>
      </div>
    </div>
  );

  function groupProps() {
    return {
      activeSessionId,
      hoveredSession,
      setHoveredSession,
      onSelectSession,
      onDeleteSession,
    };
  }
}

function SessionGroup({
  label,
  sessions,
  activeSessionId,
  hoveredSession,
  setHoveredSession,
  onSelectSession,
  onDeleteSession,
}) {
  return (
    <div>
      <p className="text-xs font-medium text-text-tertiary px-2 mb-1.5">
        {label}
      </p>
      <div className="space-y-0.5">
        {sessions.map((session) => (
          <div
            key={session.id}
            onMouseEnter={() => setHoveredSession(session.id)}
            onMouseLeave={() => setHoveredSession(null)}
            onClick={() => onSelectSession(session.id)}
            className={`group flex items-center gap-3 px-3 py-2 rounded-xl cursor-pointer transition-colors ${
              activeSessionId === session.id
                ? "bg-bg-active text-text-primary"
                : "text-text-secondary hover:bg-bg-hover"
            }`}
          >
            <Icons.Message />
            <div className="flex-1 min-w-0">
              <p className="text-sm truncate">
                {session.title || "New Conversation"}
              </p>
            </div>
            {hoveredSession === session.id && (
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  onDeleteSession(session.id);
                }}
                className="p-1 rounded-md text-text-tertiary hover:bg-bg-tertiary hover:text-red-400 transition-colors"
              >
                <Icons.Trash />
              </button>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

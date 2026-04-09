// This component is no longer used directly in the top bar.
// Agent selection is handled in the Sidebar.
// Keeping as a standalone component for potential reuse.

export default function AgentSelector({ agent, setAgent }) {
  const agents = [
    { id: "health", name: "Health Assistant", icon: "🏥" },
    { id: "sports", name: "Sports Analyst", icon: "⚡" },
    { id: "education", name: "Education Tutor", icon: "📚" },
  ];

  return (
    <div className="flex items-center gap-1">
      {agents.map((a) => (
        <button
          key={a.id}
          onClick={() => setAgent(a.id)}
          className={`px-3 py-1.5 rounded-lg text-sm transition-all ${
            agent === a.id
              ? "bg-bg-active text-text-primary"
              : "text-text-secondary hover:bg-bg-hover"
          }`}
        >
          {a.icon} {a.name}
        </button>
      ))}
    </div>
  );
}

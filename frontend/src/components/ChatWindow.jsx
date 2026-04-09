import { useEffect, useRef } from "react";
import MessageBubble from "./MessageBubble";
import { Icons } from "../utils/Icons";

export default function ChatWindow({
  messages,
  isLoading,
  streamingContent,
  statusMessage,
  agent,
}) {
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, streamingContent]);

  const getAgentInfo = () => {
    if (agent === "health")
      return { name: "Health Assistant", icon: <Icons.Health /> };
    if (agent === "sports")
      return { name: "Sports Analyst", icon: <Icons.Sports /> };
    if (agent === "education")
      return { name: "Education Tutor", icon: <Icons.Education /> };
    return { name: "AI Assistant", icon: <Icons.AI /> };
  };

  const info = getAgentInfo();

  return (
    <div className="w-full flex justify-center px-4 py-8">
      <div className="w-full max-w-4xl flex flex-col">
        {messages.length === 0 && !streamingContent && (
          <div className="flex flex-col items-center justify-center min-h-[65vh] animate-fade-in">
            <div className="w-16 h-16 rounded-2xl bg-bg-secondary border border-border-primary flex items-center justify-center text-text-primary mb-6 shadow-sm">
              {info.icon}
            </div>
            <h2 className="text-2xl font-medium text-text-primary mb-2">
              Hello.
            </h2>
            <p className="text-base text-text-secondary">
              How can I help you with {info.name.split(" ")[0].toLowerCase()}{" "}
              today?
            </p>
          </div>
        )}

        <div className="flex flex-col">
          {messages.map((msg, i) => (
            <MessageBubble key={i} message={msg} agent={agent} />
          ))}

          {streamingContent && (
            <MessageBubble
              message={{ role: "assistant", content: streamingContent }}
              agent={agent}
              isStreaming={true}
            />
          )}

          {isLoading && !streamingContent && (
            <div className="animate-fade-in mb-8">
              <StatusBar status={statusMessage} agent={agent} />
            </div>
          )}
        </div>
        <div ref={bottomRef} className="h-4" />
      </div>
    </div>
  );
}

function StatusBar({ status, agent }) {
  const isSearch = status === "searching memory";
  const text = isSearch
    ? "Searching memory..."
    : status?.startsWith("Using")
      ? status
      : "Generating response...";

  return (
    <div className="flex items-center gap-3 bg-bg-secondary w-fit px-4 py-2.5 rounded-full border border-border-primary">
      <Icons.AI />
      <div className="flex items-center gap-2 text-text-secondary text-sm font-medium">
        <span>{text}</span>
        <div className="flex gap-1 ml-1">
          <span
            className="w-1.5 h-1.5 bg-text-tertiary rounded-full animate-bounce"
            style={{ animationDelay: "0ms" }}
          />
          <span
            className="w-1.5 h-1.5 bg-text-tertiary rounded-full animate-bounce"
            style={{ animationDelay: "150ms" }}
          />
          <span
            className="w-1.5 h-1.5 bg-text-tertiary rounded-full animate-bounce"
            style={{ animationDelay: "300ms" }}
          />
        </div>
      </div>
    </div>
  );
}

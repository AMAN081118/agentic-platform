import { useState, useCallback, useRef, useEffect } from "react";
import useWebSocket from "./useWebSocket";

const MAX_MESSAGE_LENGTH = 10000;
const MAX_MESSAGES_DISPLAY = 200;

export default function useChat() {
  const API_URL = import.meta.env.DEV ? "" : import.meta.env.VITE_API_URL;
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [agent, setAgent] = useState("health");
  const [streamingContent, setStreamingContent] = useState("");
  const [statusMessage, setStatusMessage] = useState("");

  const streamingRef = useRef("");
  const loadingTimeoutRef = useRef(null);
  const { isConnected, isReconnecting, sendMessage, setMessageHandler } =
    useWebSocket();

  // Safety: auto-cancel loading state after 60 seconds
  useEffect(() => {
    if (isLoading) {
      loadingTimeoutRef.current = setTimeout(() => {
        console.warn("Loading timeout — auto-cancelling");

        // FIX: Capture the current content before clearing the ref
        const finalContent = streamingRef.current.trim();

        setIsLoading(false);
        setStreamingContent("");
        setStatusMessage("");
        streamingRef.current = "";

        setMessages((prev) => [
          ...prev,
          ...(finalContent
            ? [{ role: "assistant", content: finalContent }]
            : [
                {
                  role: "assistant",
                  content: "Response timed out. Please try again.",
                },
              ]),
        ]);
      }, 60000);

      return () => {
        if (loadingTimeoutRef.current) {
          clearTimeout(loadingTimeoutRef.current);
        }
      };
    }
  }, [isLoading]);

  const handleWsMessage = useCallback((data) => {
    switch (data.type) {
      case "connected":
        console.log("WS confirmed connected:", data.client_id);
        break;

      case "session":
        setSessionId(data.session_id);
        break;

      case "status":
        setStatusMessage(data.content || "thinking");
        break;

      case "tool":
        setStatusMessage(data.content || "Using tool...");
        break;

      case "token":
        streamingRef.current += data.content || "";
        setStreamingContent(streamingRef.current);
        setStatusMessage("");
        break;

      case "end":
        // FIX: Capture the content synchronously before React's async state update
        const finalContent = streamingRef.current.trim();

        if (finalContent) {
          setMessages((prev) => {
            const updated = [
              ...prev,
              { role: "assistant", content: finalContent },
            ];
            // Cap displayed messages
            if (updated.length > MAX_MESSAGES_DISPLAY) {
              return updated.slice(-MAX_MESSAGES_DISPLAY);
            }
            return updated;
          });
        }

        // Now it's safe to clear the refs
        streamingRef.current = "";
        setStreamingContent("");
        setStatusMessage("");
        setIsLoading(false);
        if (data.session_id) setSessionId(data.session_id);
        break;

      case "error":
        console.error("WS error:", data.content);
        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            content: "Something went wrong. Please try again.",
          },
        ]);
        streamingRef.current = "";
        setStreamingContent("");
        setStatusMessage("");
        setIsLoading(false);
        break;

      default:
        break;
    }
  }, []);

  useEffect(() => {
    setMessageHandler(handleWsMessage);
  }, [handleWsMessage, setMessageHandler]);

  const sendChat = useCallback(
    (text) => {
      if (!text.trim() || isLoading) return false;

      // Input validation
      const cleaned = text.trim().slice(0, MAX_MESSAGE_LENGTH);

      setMessages((prev) => [...prev, { role: "user", content: cleaned }]);
      setIsLoading(true);
      setStreamingContent("");
      setStatusMessage("thinking");
      streamingRef.current = "";

      // Try WebSocket first
      const sent = sendMessage({
        agent,
        message: cleaned,
        session_id: sessionId,
        user_id: "anonymous",
      });

      if (!sent) {
        console.log("WS not available, falling back to REST");
        fallbackRest(cleaned);
      }

      return true;
    },
    [agent, sessionId, isLoading, sendMessage],
  );

  const fallbackRest = async (text) => {
    try {
      setStatusMessage("thinking");
      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), 30000);

      const res = await fetch(`${API_URL}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ agent, message: text, session_id: sessionId }),
        signal: controller.signal,
      });
      clearTimeout(timeout);

      if (!res.ok) throw new Error(`HTTP ${res.status}`);

      const data = await res.json();
      if (data.session_id) setSessionId(data.session_id);

      // Simulate streaming
      const words = (data.response || "").split(" ");
      setStatusMessage("");
      for (let i = 0; i < words.length; i++) {
        await new Promise((r) => setTimeout(r, 15));
        streamingRef.current += words[i] + " ";
        setStreamingContent(streamingRef.current);
      }

      const finalRestContent = streamingRef.current.trim();
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: finalRestContent },
      ]);
    } catch (err) {
      const errorMsg =
        err.name === "AbortError"
          ? "Request timed out. Please try again."
          : "Could not reach the server. Please check your connection.";

      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: errorMsg },
      ]);
    } finally {
      setIsLoading(false);
      setStatusMessage("");
      streamingRef.current = "";
      setStreamingContent("");
    }
  };

  const loadSession = useCallback(async (id) => {
    try {
      const res = await fetch(`${API_URL}/api/sessions/${id}`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);

      const data = await res.json();
      setSessionId(id);
      setAgent(data.session.agent_type);
      setMessages(
        (data.messages || [])
          .filter((m) => m.role === "user" || m.role === "assistant")
          .map((m) => ({ role: m.role, content: m.content })),
      );
    } catch (err) {
      console.error("Failed to load session:", err);
    }
  }, []);

  const newChat = useCallback(() => {
    setSessionId(null);
    setMessages([]);
    setStreamingContent("");
    setStatusMessage("");
    setIsLoading(false);
    streamingRef.current = "";
  }, []);

  return {
    messages,
    isLoading,
    sessionId,
    agent,
    streamingContent,
    statusMessage,
    isConnected,
    isReconnecting,
    setAgent,
    setSessionId,
    sendChat,
    loadSession,
    newChat,
  };
}

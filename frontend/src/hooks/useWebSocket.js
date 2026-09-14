import { useRef, useState, useCallback, useEffect } from "react";
import { API_BASE_URL } from "../config/api";

export default function useWebSocket() {
  const wsRef = useRef(null);
  const [isConnected, setIsConnected] = useState(false);
  const [isReconnecting, setIsReconnecting] = useState(false);

  const reconnectAttempts = useRef(0);
  const reconnectTimer = useRef(null);
  const maxReconnectAttempts = 10;

  const messageHandlerRef = useRef(null);
  const mountedRef = useRef(true);

  const getWsUrl = () => {
    if (import.meta.env.DEV) {
      return "ws://localhost:8000/ws/chat";
    }

    const configuredUrl = import.meta.env.VITE_WS_URL || API_BASE_URL;

    if (!configuredUrl) {
      console.error("VITE_WS_URL or VITE_API_URL is not defined");
      return null;
    }

    try {
      const url = new URL(configuredUrl);

      // A page served over HTTPS may only open secure WebSockets. This also
      // lets VITE_WS_URL be either the Render host or the full WS endpoint.
      if (url.protocol === "http:" || url.protocol === "https:") {
        url.protocol = url.protocol === "https:" ? "wss:" : "ws:";
      }
      if (window.location.protocol === "https:" && url.protocol === "ws:") {
        url.protocol = "wss:";
      }
      if (url.pathname === "/" || url.pathname === "") {
        url.pathname = "/ws/chat";
      }
      return url.toString();
    } catch {
      console.error("VITE_WS_URL must be a complete URL");
      return null;
    }
  };

  const connect = useCallback(() => {
    if (!mountedRef.current) return;

    if (wsRef.current?.readyState === WebSocket.OPEN) return;
    if (wsRef.current?.readyState === WebSocket.CONNECTING) return;

    if (wsRef.current) {
      try {
        wsRef.current.close();
      } catch {}

      wsRef.current = null;
    }

    const url = getWsUrl();

    if (!url) {
      console.error("Cannot connect: WebSocket URL is missing");
      return;
    }

    console.log(`Connecting to ${url}...`);

    try {
      const ws = new WebSocket(url);

      ws.onopen = () => {
        if (!mountedRef.current) {
          ws.close();
          return;
        }

        console.log("WebSocket connected");

        setIsConnected(true);
        setIsReconnecting(false);
        reconnectAttempts.current = 0;
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);

          if (messageHandlerRef.current) {
            messageHandlerRef.current(data);
          }
        } catch (err) {
          console.error("WS parse error:", err);
        }
      };

      ws.onclose = (event) => {
        if (!mountedRef.current) return;

        console.log(`WebSocket closed: ${event.code}`);

        setIsConnected(false);
        wsRef.current = null;

        if (
          event.code !== 1000 &&
          reconnectAttempts.current < maxReconnectAttempts
        ) {
          setIsReconnecting(true);

          const delay = Math.min(
            1000 * Math.pow(1.5, reconnectAttempts.current),
            15000,
          );

          reconnectAttempts.current += 1;

          console.log(
            `Reconnecting in ${Math.round(delay)}ms ` +
              `(attempt ${reconnectAttempts.current})`,
          );

          reconnectTimer.current = setTimeout(() => {
            if (mountedRef.current) {
              connect();
            }
          }, delay);
        }
      };

      ws.onerror = () => {
        console.warn("WebSocket error occurred");
      };

      wsRef.current = ws;
    } catch (err) {
      console.error("Failed to create WebSocket:", err);
      setIsConnected(false);
    }
  }, []);

  const disconnect = useCallback(() => {
    if (reconnectTimer.current) {
      clearTimeout(reconnectTimer.current);
      reconnectTimer.current = null;
    }

    reconnectAttempts.current = maxReconnectAttempts;

    if (wsRef.current) {
      try {
        wsRef.current.close(1000, "Client disconnect");
      } catch {}

      wsRef.current = null;
    }

    setIsConnected(false);
    setIsReconnecting(false);
  }, []);

  const sendMessage = useCallback((data) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      try {
        wsRef.current.send(JSON.stringify(data));
        return true;
      } catch (err) {
        console.error("WS send error:", err);
        return false;
      }
    }

    return false;
  }, []);

  const setMessageHandler = useCallback((handler) => {
    messageHandlerRef.current = handler;
  }, []);

  useEffect(() => {
    mountedRef.current = true;

    const timer = setTimeout(connect, 500);

    return () => {
      mountedRef.current = false;
      clearTimeout(timer);
      disconnect();
    };
  }, []);

  return {
    isConnected,
    isReconnecting,
    sendMessage,
    setMessageHandler,
    connect,
    disconnect,
  };
}

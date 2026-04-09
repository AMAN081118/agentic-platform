import { useRef, useState, useCallback, useEffect } from "react";

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
    // In dev, connect directly to backend
    // In production, use relative path
    if (import.meta.env.DEV) {
      return "ws://localhost:8000/ws/chat";
    }
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    return `${protocol}//${window.location.host}/ws/chat`;
  };

  const connect = useCallback(() => {
    // Don't connect if already connected or component unmounted
    if (!mountedRef.current) return;
    if (wsRef.current?.readyState === WebSocket.OPEN) return;
    if (wsRef.current?.readyState === WebSocket.CONNECTING) return;

    // Clear any existing connection
    if (wsRef.current) {
      try {
        wsRef.current.close();
      } catch {}
      wsRef.current = null;
    }

    const url = getWsUrl();
    console.log(`🔌 Connecting to ${url}...`);

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

        console.log(`🔌 WebSocket closed: ${event.code}`);
        setIsConnected(false);
        wsRef.current = null;

        // Auto-reconnect unless intentionally closed
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
            `Reconnecting in ${Math.round(delay)}ms (attempt ${reconnectAttempts.current})`,
          );

          reconnectTimer.current = setTimeout(() => {
            if (mountedRef.current) connect();
          }, delay);
        }
      };

      ws.onerror = () => {
        // onclose will fire after this, so just log
        console.warn("WebSocket error occurred");
      };

      wsRef.current = ws;
    } catch (err) {
      console.error("Failed to create WebSocket:", err);
      setIsConnected(false);

      // Retry
      if (reconnectAttempts.current < maxReconnectAttempts) {
        reconnectAttempts.current += 1;
        reconnectTimer.current = setTimeout(() => {
          if (mountedRef.current) connect();
        }, 2000);
      }
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
    // Small delay to let the backend start
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

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
    if (import.meta.env.DEV) {
      return "ws://localhost:8000/ws/chat";
    }

    const url = import.meta.env.VITE_WS_URL;

    if (!url) {
      console.error("VITE_WS_URL is not defined");
      return null;
    }

    return url;
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

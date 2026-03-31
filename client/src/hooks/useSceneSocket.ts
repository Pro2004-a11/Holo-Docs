import { useEffect, useRef, useState, useCallback } from 'react';
import type { SceneState } from '../types/bridge';

/**
 * Connects to the orchestrator's scene state WebSocket.
 * Receives scene updates at ~30Hz and exposes the latest state.
 */
export function useSceneSocket(sessionId: string, orchestratorWsUrl: string) {
  const [sceneState, setSceneState] = useState<SceneState | null>(null);
  const [connected, setConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);

  const connect = useCallback(() => {
    const url = `${orchestratorWsUrl}/ws/scene/${sessionId}`;
    const ws = new WebSocket(url);
    wsRef.current = ws;

    ws.onopen = () => {
      console.log('[scene] WS connected to orchestrator');
      setConnected(true);
    };

    ws.onmessage = (event) => {
      try {
        const state: SceneState = JSON.parse(event.data);
        setSceneState(state);
      } catch (e) {
        console.warn('[scene] Failed to parse state:', e);
      }
    };

    ws.onerror = (e) => console.error('[scene] WS error:', e);
    ws.onclose = () => {
      console.log('[scene] WS closed');
      setConnected(false);
    };
  }, [sessionId, orchestratorWsUrl]);

  const disconnect = useCallback(() => {
    wsRef.current?.close();
  }, []);

  useEffect(() => {
    return () => disconnect();
  }, [disconnect]);

  return { sceneState, connected, connect, disconnect };
}

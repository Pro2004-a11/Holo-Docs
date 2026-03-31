import { useState, useCallback } from 'react';
import { Scene } from './canvas/Scene';
import { GestureCursor } from './hud/GestureCursor';
import { StatusBar } from './hud/StatusBar';
import { useWebcamStream } from './hooks/useWebcamStream';
import { useSceneSocket } from './hooks/useSceneSocket';
import { useGestureState } from './hooks/useGestureState';
import { GlassPanel } from './hud/GlassPanel';

// Generate a stable session ID per browser tab
const SESSION_ID = crypto.randomUUID();

// Service URLs — in production these come from env vars
const VISION_WS_URL = 'ws://localhost:8001';
const ORCHESTRATOR_WS_URL = 'ws://localhost:8080';

export function App() {
  const [started, setStarted] = useState(false);

  const webcam = useWebcamStream(SESSION_ID, VISION_WS_URL);
  const scene = useSceneSocket(SESSION_ID, ORCHESTRATOR_WS_URL);
  const gesture = useGestureState(scene.sceneState);

  const handleStart = useCallback(async () => {
    await webcam.start();
    scene.connect();
    setStarted(true);
  }, [webcam, scene]);

  const handleStop = useCallback(() => {
    webcam.stop();
    scene.disconnect();
    setStarted(false);
  }, [webcam, scene]);

  return (
    <div style={{ width: '100vw', height: '100vh', position: 'relative', background: '#0a0a0f' }}>
      {/* 3D Canvas */}
      <Scene
	    sceneState={scene.sceneState}
		cursorX={gesture.cursorX}
		cursorY={gesture.cursorY}
		isPinching={gesture.activeGesture === 'PINCH'}
	  />

      {/* Gesture cursor overlay */}
      <GestureCursor
        x={gesture.cursorX}
        y={gesture.cursorY}
        gesture={gesture.activeGesture}
        isTracking={gesture.isTracking}
      />

      {/* Start/stop button */}
      {!started ? (
        <GlassPanel
          style={{
            position: 'absolute',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            padding: '32px 48px',
            textAlign: 'center',
            cursor: 'pointer',
            zIndex: 200,
          }}
        >
          <h1
            style={{
              color: '#e0e0ff',
              fontSize: '28px',
              fontWeight: 300,
              marginBottom: 16,
              fontFamily: 'system-ui',
            }}
          >
            Holo-Docs
          </h1>
          <p
            style={{
              color: 'rgba(255,255,255,0.5)',
              fontSize: '14px',
              marginBottom: 24,
              fontFamily: 'monospace',
            }}
          >
            spatial document interface
          </p>
          <button
            onClick={handleStart}
            style={{
              background: '#5a4aff',
              color: '#fff',
              border: 'none',
              padding: '12px 32px',
              borderRadius: 8,
              fontSize: '16px',
              cursor: 'pointer',
              fontFamily: 'system-ui',
            }}
          >
            Start Session
          </button>
        </GlassPanel>
      ) : (
        <button
          onClick={handleStop}
          style={{
            position: 'absolute',
            top: 16,
            right: 16,
            background: 'rgba(255,255,255,0.1)',
            color: 'rgba(255,255,255,0.6)',
            border: '1px solid rgba(255,255,255,0.1)',
            padding: '6px 16px',
            borderRadius: 6,
            fontSize: '12px',
            cursor: 'pointer',
            fontFamily: 'monospace',
            zIndex: 50,
          }}
        >
          stop
        </button>
      )}

      {/* Status bar */}
      {started && (
        <StatusBar
          connected={scene.connected}
          frameSeq={scene.sceneState?.frame_seq ?? 0}
          gesture={gesture.activeGesture}
          sessionId={SESSION_ID}
        />
      )}
    </div>
  );
}

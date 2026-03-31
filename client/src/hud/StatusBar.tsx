import { GlassPanel } from './GlassPanel';

interface StatusBarProps {
  connected: boolean;
  frameSeq: number;
  gesture: string;
  sessionId: string;
}

/**
 * Bottom status bar showing connection state, frame count, and active gesture.
 */
export function StatusBar({ connected, frameSeq, gesture, sessionId }: StatusBarProps) {
  return (
    <GlassPanel
      style={{
        position: 'absolute',
        bottom: 16,
        left: '50%',
        transform: 'translateX(-50%)',
        padding: '8px 20px',
        display: 'flex',
        gap: 24,
        fontSize: '12px',
        fontFamily: 'monospace',
        color: 'rgba(255,255,255,0.7)',
        zIndex: 50,
      }}
    >
      {/* Connection indicator */}
      <span>
        <span
          style={{
            display: 'inline-block',
            width: 8,
            height: 8,
            borderRadius: '50%',
            background: connected ? '#4ade80' : '#f87171',
            marginRight: 6,
          }}
        />
        {connected ? 'connected' : 'disconnected'}
      </span>

      <span>frame: {frameSeq}</span>
      <span>gesture: {gesture.toLowerCase()}</span>
      <span style={{ opacity: 0.4 }}>{sessionId.slice(0, 8)}</span>
    </GlassPanel>
  );
}

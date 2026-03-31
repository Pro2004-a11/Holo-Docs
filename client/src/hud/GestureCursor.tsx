import type { GestureType } from '../types/bridge';

interface GestureCursorProps {
  x: number;
  y: number;
  gesture: GestureType;
  isTracking: boolean;
}

const GESTURE_LABELS: Record<GestureType, string> = {
  PINCH: 'pinch',
  PINCH_RELEASE: 'release',
  POINT: 'point',
  SWIPE_LEFT: 'swipe-L',
  SWIPE_RIGHT: 'swipe-R',
  OPEN_PALM: 'palm',
  IDLE: '',
};

/**
 * Hand-tracked cursor overlay — follows the hand position on screen.
 * Shows gesture type and visual ring feedback.
 */
export function GestureCursor({ x, y, gesture, isTracking }: GestureCursorProps) {
  if (!isTracking) return null;

  const isPinching = gesture === 'PINCH';
  const ringSize = isPinching ? 24 : 32;
  const ringColor = isPinching ? '#5a4aff' : 'rgba(255,255,255,0.35)';

  return (
    <div
      style={{
        position: 'absolute',
        left: `${x * 100}%`,
        top: `${y * 100}%`,
        transform: 'translate(-50%, -50%)',
        pointerEvents: 'none',
        zIndex: 100,
        transition: 'left 0.05s ease-out, top 0.05s ease-out',
      }}
    >
      {/* Ring */}
      <div
        style={{
          width: ringSize,
          height: ringSize,
          borderRadius: '50%',
          border: `2px solid ${ringColor}`,
          background: isPinching ? 'rgba(90,74,255,0.15)' : 'transparent',
          transition: 'all 0.1s ease-out',
        }}
      />
      {/* Label */}
      {gesture !== 'IDLE' && (
        <div
          style={{
            position: 'absolute',
            top: ringSize + 4,
            left: '50%',
            transform: 'translateX(-50%)',
            fontSize: '10px',
            color: 'rgba(255,255,255,0.6)',
            whiteSpace: 'nowrap',
            fontFamily: 'monospace',
          }}
        >
          {GESTURE_LABELS[gesture]}
        </div>
      )}
    </div>
  );
}

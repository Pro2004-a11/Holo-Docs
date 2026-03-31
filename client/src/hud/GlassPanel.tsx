import type { ReactNode } from 'react';
import '../styles/glass.css';

interface GlassPanelProps {
  children: ReactNode;
  className?: string;
  style?: React.CSSProperties;
}

/**
 * Glassmorphism overlay container — frosted glass effect over the 3D canvas.
 */
export function GlassPanel({ children, className = '', style }: GlassPanelProps) {
  return (
    <div className={`glass-panel ${className}`} style={style}>
      {children}
    </div>
  );
}

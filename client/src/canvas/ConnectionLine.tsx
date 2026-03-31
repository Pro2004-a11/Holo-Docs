import { useMemo } from 'react';
import * as THREE from 'three';

interface ConnectionLineProps {
  from: [number, number, number];
  to: [number, number, number];
}

/**
 * A glowing line connecting two document nodes in the knowledge graph.
 */
export function ConnectionLine({ from, to }: ConnectionLineProps) {
  const geometry = useMemo(() => {
    const points = [new THREE.Vector3(...from), new THREE.Vector3(...to)];
    return new THREE.BufferGeometry().setFromPoints(points);
  }, [from, to]);

  return (
    <line geometry={geometry}>
      <lineBasicMaterial color="#4a4aff" transparent opacity={0.4} linewidth={1} />
    </line>
  );
}

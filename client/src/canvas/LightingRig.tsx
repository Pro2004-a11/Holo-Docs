import { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import type { SceneLighting } from '../types/bridge';

interface LightingRigProps {
  lighting: SceneLighting | null;
}

/**
 * Dynamic directional light that follows the CV-estimated light direction.
 * Lerps position/intensity for smooth transitions.
 */
export function LightingRig({ lighting }: LightingRigProps) {
  const lightRef = useRef<THREE.DirectionalLight>(null!);
  const targetDir = useRef(new THREE.Vector3(0, -1, 0.5));
  const targetIntensity = useRef(0.8);

  if (lighting) {
    targetDir.current.set(...lighting.direction);
    targetIntensity.current = lighting.intensity;
  }

  useFrame(() => {
    if (lightRef.current) {
      // Lerp light position toward target direction (scaled up for distance)
      const target = targetDir.current.clone().multiplyScalar(5);
      lightRef.current.position.lerp(target, 0.1);
      // Lerp intensity
      lightRef.current.intensity += (targetIntensity.current - lightRef.current.intensity) * 0.1;
    }
  });

  // Convert dominant_color to Three.js color
  const color = lighting
    ? new THREE.Color(
        lighting.color[0] / 255,
        lighting.color[1] / 255,
        lighting.color[2] / 255
      )
    : new THREE.Color(1, 1, 1);

  return (
    <directionalLight
      ref={lightRef}
      position={[0, 5, 2.5]}
      intensity={0.8}
      color={color}
      castShadow={false}
    />
  );
}

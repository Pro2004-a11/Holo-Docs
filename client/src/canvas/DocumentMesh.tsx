import { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import { Text } from '@react-three/drei';
import * as THREE from 'three';
import type { SceneObject } from '../types/bridge';

interface DocumentMeshProps {
  sceneObject: SceneObject;
}

// Visual feedback colors per state
const STATE_COLORS: Record<string, string> = {
  IDLE: '#2a2a4a',
  HOVERED: '#3a3a6a',
  GRABBED: '#5a4aff',
};

/**
 * 3D document card — a rounded box with title text.
 * Position/rotation driven by scene state from orchestrator.
 * Lerps position for smooth movement.
 */
export function DocumentMesh({ sceneObject }: DocumentMeshProps) {
  const meshRef = useRef<THREE.Mesh>(null!);
  const targetPos = useRef(new THREE.Vector3(...sceneObject.position));

  // Update target position when scene state changes
  targetPos.current.set(...sceneObject.position);

  // Smooth interpolation toward target position
  useFrame(() => {
    if (meshRef.current) {
      meshRef.current.position.lerp(targetPos.current, 0.15);
    }
  });

  const color = STATE_COLORS[sceneObject.state] ?? STATE_COLORS.IDLE;
  const emissiveIntensity = sceneObject.state === 'GRABBED' ? 0.3 : 0.05;

  return (
    <group>
      <mesh
        ref={meshRef}
        position={sceneObject.position}
        rotation={sceneObject.rotation.map((d) => (d * Math.PI) / 180) as [number, number, number]}
        scale={sceneObject.scale}
      >
        {/* Document card: thin box */}
        <boxGeometry args={[1.2, 0.8, 0.02]} />
        <meshStandardMaterial
          color={color}
          emissive={color}
          emissiveIntensity={emissiveIntensity}
          transparent
          opacity={0.85}
          roughness={0.3}
          metalness={0.1}
        />
      </mesh>

      {/* Title text floating in front of the card */}
      <Text
        position={[
          sceneObject.position[0],
          sceneObject.position[1],
          sceneObject.position[2] + 0.02,
        ]}
        fontSize={0.08}
        color="#e0e0ff"
        anchorX="center"
        anchorY="middle"
        maxWidth={1.0}
      >
        {sceneObject.metadata.title}
      </Text>
    </group>
  );
}

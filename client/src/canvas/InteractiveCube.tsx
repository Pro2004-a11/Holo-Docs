import { useRef, useState } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

export function InteractiveCube({ cursorX, cursorY, isPinching }: { cursorX: number, cursorY: number, isPinching: boolean }) {
  const meshRef = useRef<THREE.Mesh>(null!);
  const [pos, setPos] = useState<[number, number, number]>([0, 1, 0]);

  useFrame((state) => {
  if (!meshRef.current) return;

  // 1. Convert hand coords to 3D space
  const vector = new THREE.Vector3((cursorX * 2) - 1, -(cursorY * 2) + 1, 0.5);
  vector.unproject(state.camera);
  const dir = vector.sub(state.camera.position).normalize();
  const targetPosition = state.camera.position.clone().add(dir.multiplyScalar(3));

  // 2. ONLY move if pinching
  if (isPinching) {
    // We use a faster lerp (0.3) so it feels more responsive than the docs
    meshRef.current.position.lerp(targetPosition, 0.3);
    meshRef.current.scale.lerp(new THREE.Vector3(1.3, 1.3, 1.3), 0.2);
  } else {
    // Return to "Home" or stay put
    meshRef.current.scale.lerp(new THREE.Vector3(1, 1, 1), 0.1);
  }
});

  return (
    <mesh ref={meshRef} position={pos}>
      <boxGeometry args={[0.5, 0.5, 0.5]} />
      <meshStandardMaterial color={isPinching ? "hotpink" : "yellow"} />
    </mesh>
  );
}
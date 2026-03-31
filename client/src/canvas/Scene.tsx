import { Canvas } from '@react-three/fiber';
import { OrbitControls } from '@react-three/drei';
import { DocumentMesh } from './DocumentMesh';
import { ConnectionLine } from './ConnectionLine';
import { LightingRig } from './LightingRig';
import { InteractiveCube } from './InteractiveCube';
import type { SceneState } from '../types/bridge';
import { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

// 1. THE DYNAMIC GRID COMPONENT
export function CyberGrid() {
  const gridRef = useRef<THREE.Mesh>(null!);

  useFrame((state) => {
    const t = state.clock.getElapsedTime();
    if (gridRef.current) {
      (gridRef.current.material as THREE.ShaderMaterial).uniforms.uTime.value = t;
    }
  });

  return (
    <mesh ref={gridRef} rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.01, 0]}>
      <planeGeometry args={[20, 20]} />
      <shaderMaterial
        transparent
        uniforms={{
          uTime: { value: 0 },
          uColor: { value: new THREE.Color('#00ffff') },
        }}
        vertexShader={`
          varying vec2 vUv;
          void main() {
            vUv = uv;
            gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
          }
        `}
        fragmentShader={`
          varying vec2 vUv;
          uniform float uTime;
          uniform vec3 uColor;

          void main() {
            vec2 grid = abs(fract(vUv * 40.0 - 0.5) - 0.5) / fwidth(vUv * 40.0);
            float line = min(grid.x, grid.y);
            float baseGrid = 1.0 - min(line, 1.0);

            float scan = smoothstep(0.9, 1.0, 1.0 - abs(fract(vUv.y - uTime * 0.2) - 0.5) * 2.0);
            
            vec3 finalColor = uColor * (baseGrid * 0.2 + scan * 0.8);
            float alpha = baseGrid * 0.1 + scan * 0.5;

            gl_FragColor = vec4(finalColor, alpha);
          }
        `}
      />
    </mesh>
  );
}

// 2. THE MAIN SCENE
interface SceneProps {
  sceneState: SceneState | null;
  cursorX: number; 
  cursorY: number;
  isPinching: boolean; // Added this missing prop
}

export function Scene({ sceneState, cursorX, cursorY, isPinching }: SceneProps) {
  const objects = sceneState?.scene_objects ?? [];
  const lighting = sceneState?.lighting ?? null;

  return (
    <Canvas 
      camera={{ position: [0, 1, 3], fov: 60 }}
      style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%' }}
    >
      <ambientLight intensity={0.5} />
      <LightingRig lighting={lighting} />

      {/* The Dynamic Animated Grid */}
      <CyberGrid />

      {/* The Interactive Cube - Only one instance needed */}
      <InteractiveCube 
        cursorX={cursorX} 
        cursorY={cursorY} 
        isPinching={isPinching} 
      />

      {/* Demo documents - locked so they don't fight the cube */}
      {objects.map((obj) => (
        <DocumentMesh 
          key={obj.id} 
          sceneObject={obj} 
          isLocked={true}
        />
      ))}

      {/* Connection lines */}
      {objects.map((obj) =>
        (obj.metadata.connections ?? []).map((targetId) => {
          const target = objects.find((o) => o.id === targetId);
          if (!target) return null;
          return (
            <ConnectionLine
              key={`${obj.id}-${targetId}`}
              from={obj.position}
              to={target.position}
            />
          );
        })
      )}

      <OrbitControls enablePan={false} enableZoom={false} />
    </Canvas>
  );
}
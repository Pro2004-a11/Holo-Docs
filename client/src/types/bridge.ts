/**
 * Bridge protocol TypeScript types — mirrors Python schemas and Java DTOs.
 */

export type GestureType =
  | 'PINCH'
  | 'PINCH_RELEASE'
  | 'POINT'
  | 'SWIPE_LEFT'
  | 'SWIPE_RIGHT'
  | 'OPEN_PALM'
  | 'IDLE';

export type Handedness = 'LEFT' | 'RIGHT';

export interface Gesture {
  type: GestureType;
  confidence: number;
  pinch_distance?: number;
}

export interface HandLandmarks {
  wrist: [number, number, number];
  index_tip: [number, number, number];
  thumb_tip: [number, number, number];
  middle_tip: [number, number, number];
  ring_tip: [number, number, number];
  pinky_tip: [number, number, number];
  palm_center: [number, number, number];
}

export interface HandData {
  handedness: Handedness;
  landmarks: HandLandmarks;
  gesture: Gesture;
}

export interface HeadPose {
  pitch: number;
  yaw: number;
  roll: number;
}

export interface LightVector {
  direction: [number, number, number];
  intensity: number;
  dominant_color: [number, number, number];
}

// ── Scene State (from orchestrator) ──

export interface SceneObject {
  id: string;
  type: string;
  position: [number, number, number];
  rotation: [number, number, number];
  scale: [number, number, number];
  state: 'IDLE' | 'HOVERED' | 'GRABBED';
  grabbed_by: string | null;
  metadata: {
    title: string;
    node_type: string;
    connections: string[];
  };
}

export interface SceneLighting {
  direction: [number, number, number];
  intensity: number;
  color: [number, number, number];
}

export interface HudState {
  cursor_position: [number, number];
  active_gesture: GestureType;
  feedback_text: string | null;
}

export interface SceneState {
  $schema: string;
  version: string;
  session_id: string;
  timestamp: number;
  frame_seq: number;
  scene_objects: SceneObject[];
  lighting: SceneLighting;
  hud: HudState;
}

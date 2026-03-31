# Holo-Docs Implementation Plan

## Overview
Spatial computing web app: gesture-driven 3D document interface powered by real-time computer vision.

**Stack:** Python/FastAPI (CV) → Java 21/Spring Boot (Orchestrator) → React/Three.js (Render)

---

## Architecture Summary

```
Browser (webcam frames) ──WS──> Python/MediaPipe ──HTTP POST──> Java/Spring Boot ──WS──> Browser (Three.js)
```

- Vision service is stateless — processes frames, emits gesture events
- Orchestrator manages session state, scene graph, knowledge graph
- Frontend renders 3D canvas + glassmorphism HUD
- Target: <33ms end-to-end latency per frame

---

## Phase 1: Week 1 — Plumbing

### 1.1 Scaffold Vision Service (Python)
- [ ] `vision/pyproject.toml` — FastAPI, uvicorn, mediapipe, websockets, httpx
- [ ] `vision/src/main.py` — FastAPI app with WebSocket endpoint for frame ingestion
- [ ] `vision/src/schemas.py` — Pydantic models for GestureEvent, HandData, LightVector
- [ ] `vision/src/frame_processor.py` — MediaPipe Hands + Face Mesh initialization
- [ ] `vision/src/gesture_classifier.py` — Landmarks → gesture enum (PINCH, POINT, SWIPE, etc.)
- [ ] `vision/src/light_estimator.py` — Face mesh normals → estimated light direction
- [ ] `vision/src/bridge_client.py` — HTTP POST gesture events to orchestrator
- [ ] `vision/Dockerfile`

### 1.2 Scaffold Orchestrator (Java 21)
- [ ] `server/pom.xml` — Spring Boot 3.2+, WebSocket, Jackson
- [ ] `server/src/.../HoloDocsApplication.java` — Main entry
- [ ] `server/src/.../config/WebSocketConfig.java` — WS endpoint registration
- [ ] `server/src/.../bridge/BridgeSchemas.java` — DTOs matching bridge protocol
- [ ] `server/src/.../bridge/GestureEventController.java` — POST /api/gesture-event
- [ ] `server/src/.../bridge/SceneWebSocketHandler.java` — WS push to browser
- [ ] `server/src/.../session/SessionManager.java` — Virtual thread per session
- [ ] `server/src/.../session/SessionState.java` — Per-session scene state
- [ ] `server/src/.../scene/SceneGraph.java` — Object positions, transforms
- [ ] `server/src/.../scene/GestureInterpreter.java` — Gesture → scene mutation
- [ ] `server/src/.../graph/KnowledgeGraphService.java` — Stub for knowledge graph
- [ ] `server/src/.../graph/DocumentNode.java` — Graph node model
- [ ] `server/Dockerfile`

### 1.3 Scaffold Frontend (React + Three.js)
- [ ] `client/package.json` — React 18, Three.js, @react-three/fiber, @react-three/drei, vite
- [ ] `client/vite.config.ts`
- [ ] `client/index.html`
- [ ] `client/src/main.tsx` — React entry
- [ ] `client/src/App.tsx` — Layout: canvas + HUD overlay
- [ ] `client/src/hooks/useWebcamStream.ts` — getUserMedia, frame capture, WS send
- [ ] `client/src/hooks/useSceneSocket.ts` — WS connection to orchestrator
- [ ] `client/src/hooks/useGestureState.ts` — Derived gesture state from scene updates
- [ ] `client/src/canvas/Scene.tsx` — R3F canvas wrapper
- [ ] `client/src/canvas/DocumentMesh.tsx` — 3D document card component
- [ ] `client/src/canvas/ConnectionLine.tsx` — Graph edge visualization
- [ ] `client/src/canvas/LightingRig.tsx` — Dynamic lighting from CV data
- [ ] `client/src/hud/GlassPanel.tsx` — Glassmorphism overlay container
- [ ] `client/src/hud/GestureCursor.tsx` — Hand-tracked cursor element
- [ ] `client/src/hud/StatusBar.tsx` — Tracking status + latency display
- [ ] `client/src/styles/glass.css` — Glassmorphism design tokens
- [ ] `client/src/styles/shaders/hologram.glsl` — Custom shader for doc cards
- [ ] `client/src/types/bridge.ts` — TypeScript types matching bridge protocol

### 1.4 Infrastructure
- [ ] `docker-compose.yml` — All 3 services + optional Neo4j
- [ ] Verify `docker-compose up` boots all services cleanly
- [ ] End-to-end: browser frame → Python log → Java log → browser console

---

## Phase 2: Week 2 — The Loop

### 2.1 Frame Pipeline
- [ ] Browser captures at 30fps, downscales to 320x240, JPEG compresses
- [ ] Vision WS receives frames, runs MediaPipe, returns landmarks
- [ ] Gesture classifier detects PINCH with confidence threshold

### 2.2 Scene State Loop
- [ ] Java pushes scene state at 30Hz over WS
- [ ] Three.js renders cube from scene state (position, rotation, scale)
- [ ] Pinch gesture → grab state in Java → cube follows hand position
- [ ] Cube moves with hand in real-time

---

## Phase 3: Week 3 — Polish the Slice

### 3.1 Interaction
- [ ] PINCH_RELEASE drops object at current position
- [ ] Smooth interpolation (lerp) on object movement

### 3.2 Environmental Lighting
- [ ] Light vector estimation from face mesh shading
- [ ] Three.js directional light matches CV-estimated direction
- [ ] Intensity and color temperature adaptation

### 3.3 HUD
- [ ] Glassmorphism cursor following hand position
- [ ] Gesture state indicator (tracking / pinching / lost)
- [ ] Latency display (p50/p95 per hop)

---

## Phase 4: Week 4 — Stabilize & Demo

### 4.1 Edge Cases
- [ ] Hand lost → cursor fades, objects stay put
- [ ] Hand re-entry → smooth resume, no teleportation
- [ ] Multi-hand → primary hand selection logic

### 4.2 Visual Upgrade
- [ ] Replace cube with textured document card mesh
- [ ] Hologram shader effect on cards
- [ ] Head-pose parallax (subtle canvas shift)

### 4.3 Demo
- [ ] Instrument full pipeline latency
- [ ] Record demo video
- [ ] Document findings + Phase 2 planning

---

## Bridge Protocol Reference

### Gesture Event (Vision → Orchestrator)
```json
{
  "$schema": "bridge/gesture-event",
  "version": "1.0",
  "sessionId": "uuid",
  "timestamp": 1709000000000,
  "frameSeq": 4821,
  "hands": [{
    "handedness": "RIGHT",
    "landmarks": {
      "wrist": [0.52, 0.71, -0.03],
      "indexTip": [0.61, 0.45, -0.08],
      "thumbTip": [0.48, 0.52, -0.05]
    },
    "gesture": {
      "type": "PINCH",
      "confidence": 0.93,
      "pinchDistance": 0.012
    }
  }],
  "headPose": { "pitch": -5.2, "yaw": 12.1, "roll": -0.8 },
  "lightVector": {
    "direction": [0.3, -0.7, 0.5],
    "intensity": 0.82,
    "dominantColor": [255, 244, 230]
  }
}
```

### Scene State (Orchestrator → Browser)
```json
{
  "$schema": "bridge/scene-state",
  "version": "1.0",
  "sessionId": "uuid",
  "timestamp": 1709000000050,
  "frameSeq": 4821,
  "sceneObjects": [{
    "id": "doc-node-1",
    "type": "DOCUMENT",
    "position": [0.0, 1.2, -2.0],
    "rotation": [0, 15.5, 0],
    "scale": [1.0, 1.0, 1.0],
    "state": "GRABBED",
    "grabbedBy": "RIGHT",
    "metadata": {
      "title": "Q4 Architecture Review",
      "nodeType": "wiki",
      "connections": ["doc-node-3", "doc-node-7"]
    }
  }],
  "lighting": {
    "direction": [0.3, -0.7, 0.5],
    "intensity": 0.82,
    "color": [255, 244, 230]
  },
  "hud": {
    "cursorPosition": [0.61, 0.45],
    "activeGesture": "PINCH",
    "feedbackText": null
  }
}
```

### Gesture Types
| Gesture | Trigger | Scene Action |
|---------|---------|-------------|
| PINCH | thumb+index < 0.02 | Grab/select |
| PINCH_RELEASE | was pinching, now > 0.04 | Drop/deselect |
| POINT | index extended, rest curled | Highlight/hover |
| SWIPE_LEFT | palm -X > 0.15 in 200ms | Navigate back |
| SWIPE_RIGHT | palm +X > 0.15 in 200ms | Navigate forward |
| OPEN_PALM | all fingers out, facing cam | Reset/menu |
| IDLE | no motion | No action |

---

## Key Decisions
- **Vision → Orchestrator**: HTTP POST (not WebSocket) — vision is stateless, simpler
- **Frame transport**: Binary WebSocket (JPEG) — browser direct to Python, skip Java
- **Frame resolution**: 320x240 — sufficient for MediaPipe, keeps payload ~15KB
- **State push rate**: 30Hz — matches input rate, smooth enough for Three.js
- **Knowledge graph**: Deferred to Phase 2 — stub interface in Week 1
- **gRPC**: Evaluate end of Week 1 if HTTP latency is a bottleneck

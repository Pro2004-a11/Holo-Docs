# Holo-Docs 🌌
> **Gesture-Driven 3D Knowledge Graph for Spatial Computing**

[![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)](https://www.python.org/)
[![Java](https://img.shields.io/badge/java-%23ED8B00.svg?style=for-the-badge&logo=openjdk&logoColor=white)](https://www.oracle.com/java/)
[![Spring Boot](https://img.shields.io/badge/Spring_Boot-6DB33F?style=for-the-badge&logo=spring-boot&logoColor=white)](https://spring.io/projects/spring-boot)
[![Three.js](https://img.shields.io/badge/threejs-black?style=for-the-badge&logo=three.js&logoColor=white)](https://threejs.org/)
[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)

---

### 🖥️ Performance Environment
![GPU](https://img.shields.io/badge/GPU-RTX_4070_Ti_Verified-green?style=flat-square&logo=nvidia)
![CUDA](https://img.shields.io/badge/CUDA-13.2-76B900?style=flat-square&logo=nvidia)
![OS](https://img.shields.io/badge/OS-Windows_11-0078D4?style=flat-square&logo=windows-11)
![Memory](https://img.shields.io/badge/RAM-64GB_DDR5-blue?style=flat-square)

---

Holo-Docs 

A Gesture-Driven 3D Graph for Spatial Computing
Holo-Docs is a high-performance spatial computing web application that replaces traditional "point-and-click" workflows with a gesture-driven 3D interface. a real-time computer vision and a distributed architecture, it allows users to manipulate document nodes in a 3D scene using natural hand movements.

Key Features

Real-Time Gesture Orchestration: Low-latency (<33ms) pipeline for pinch-to-grab, swiping, and pointing interactions.
Environmental Lighting Estimation: CV-driven light vector estimation that matches virtual 3D lighting to your real-world room conditions.

Distributed Architecture:

A stateless Python vision service coupled with a high-concurrency Java/Spring Boot orchestrator.
Holographic HUD: A React-based "Glassmorphism" interface providing real-time tracking feedback and system status.

responsiveness:

Vision Service (Python): Processes raw webcam frames via MediaPipe to emit gesture events and light vectors.
Orchestrator (Java 21): Manages the session state, scene graph transforms, and knowledge graph logic using Spring Boot.
Frontend (React/Three.js): Renders the 3D environment and custom GLSL hologram shaders at 30Hz.

Tech Stack

Frontend: React 18, Three.js, @react-three/fiber, Vite.
Orchestrator: Java 21, Spring Boot 3.2, WebSockets (JSR 356).
Vision: Python 3.10+, FastAPI, MediaPipe, OpenCV.
Infrastructure: Docker Compose, Neo4j (Planned).

Quick Start (Development)
Requirements: Docker & Docker Compose, Webcam.
Clone the repository:
Bash
git clone https://github.com/your-username/holo-docs.git
cd holo-docs




Boot the stack:
Bash
docker-compose up --build




Access the interface:
Open http://localhost:5173 in a browser that supports getUserMedia.

Suggested Repository Structure
Since your plan involves three distinct environments, I recommend a monorepo structure:
Plaintext

## 📂 Project Structure

```text
/holo-docs
├── client/              # React + Three.js + Vite
│   ├── src/canvas/      # 3D components (DocumentMesh, LightingRig)
│   ├── src/hud/         # Glassmorphism UI components
│   └── src/hooks/       # useWebcamStream, useSceneSocket
├── server/              # Java 21 / Spring Boot Orchestrator
│   ├── src/bridge/      # DTOs and Controllers for CV data
│   ├── src/session/     # Virtual thread-based session management
│   └── src/scene/       # SceneGraph and GestureInterpreter logic
├── vision/              # Python / FastAPI Vision Service
│   ├── src/processors/  # MediaPipe Hand/Face mesh logic
│   └── src/classifiers/ # Landmark-to-Gesture logic
├── docker-compose.yml   # Multi-service orchestration
└── README.md



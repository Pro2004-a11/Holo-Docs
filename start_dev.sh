#!/bin/bash
# Holo-Docs dev startup — runs all 3 services without Docker.
# Usage: bash start_dev.sh

set -e

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
PIDS=()

cleanup() {
    echo ""
    echo "[startup] Shutting down..."
    for pid in "${PIDS[@]}"; do
        kill "$pid" 2>/dev/null || true
    done
    wait 2>/dev/null
    echo "[startup] Done."
}
trap cleanup EXIT INT TERM

echo "=== Holo-Docs Dev Server ==="
echo ""

# 1. Install Python deps if needed
if ! python3 -c "import fastapi" 2>/dev/null; then
    echo "[startup] Installing Python dependencies..."
    pip3 install --user fastapi uvicorn[standard] websockets httpx mediapipe opencv-python-headless pydantic numpy 2>&1 | tail -1
fi

# 2. Install Node deps if needed
if [ ! -d "$PROJECT_DIR/client/node_modules" ]; then
    echo "[startup] Installing Node dependencies..."
    cd "$PROJECT_DIR/client" && npm install 2>&1 | tail -3
    cd "$PROJECT_DIR"
fi

echo ""
echo "[startup] Starting services..."
echo ""

# 3. Start orchestrator mock (port 8080)
echo "[startup] → Orchestrator mock on :8080"
cd "$PROJECT_DIR"
python3 -m uvicorn server.orchestrator_mock:app --host 0.0.0.0 --port 8080 --log-level info &
PIDS+=($!)

sleep 1

# 4. Start vision service (port 8001)
echo "[startup] → Vision service on :8001"
cd "$PROJECT_DIR"
ORCHESTRATOR_URL=http://localhost:8080 python3 -m uvicorn vision.src.main:app --host 0.0.0.0 --port 8001 --log-level info &
PIDS+=($!)

sleep 1

# 5. Start frontend dev server (port 3000)
echo "[startup] → Frontend on :3000"
cd "$PROJECT_DIR/client"
npx vite --host 0.0.0.0 --port 3000 &
PIDS+=($!)

echo ""
echo "=== All services running ==="
echo "  Frontend:     http://localhost:3000"
echo "  Vision WS:    ws://localhost:8001/ws/frames/{sessionId}"
echo "  Orchestrator: http://localhost:8080/api/health"
echo ""
echo "Press Ctrl+C to stop all services."
echo ""

wait

@echo off
SETLOCAL EnableDelayedExpansion

REM Get the directory where the script is located
set PROJECT_DIR=%~dp0
set PYTHON="C:\Users\yosir\AppData\Local\Programs\Python\Python312\python.exe"

echo === Holo-Docs Dev Server: Portable Edition ===
echo.

REM --- 1. Python & Environment Setup ---
if exist "venv\Scripts\python.exe" (
    set PYTHON="%PROJECT_DIR%venv\Scripts\python.exe"
    echo [System] Using existing virtual environment.
) else (
    echo [System] No venv found. Creating one for portability...
    python -m venv venv
    set PYTHON="%PROJECT_DIR%venv\Scripts\python.exe"
)

REM --- 2. Dependency Check (Fixes cv2, mediapipe, and uvicorn errors) ---
echo [System] Syncing dependencies...
%PYTHON% -m pip install --upgrade pip >nul
%PYTHON% -m pip install uvicorn[standard] fastapi opencv-python mediapipe websockets python-multipart >nul
echo [System] Dependencies ready.

REM --- 3. Launch Services ---

REM Terminal 1: Orchestrator mock on :8080
echo [Launch] Starting Orchestrator...
start "Holo-Docs: Orchestrator :8080" cmd /k "%PYTHON% -m uvicorn server.orchestrator_mock:app --host 0.0.0.0 --port 8080 --log-level info"

timeout /t 2 /nobreak >nul

REM Terminal 2: Vision service on :8001
echo [Launch] Starting Vision Service...
start "Holo-Docs: Vision :8001" cmd /k "set ORCHESTRATOR_URL=http://localhost:8080 && %PYTHON% -m uvicorn vision.src.main:app --host 0.0.0.0 --port 8001 --log-level info"

timeout /t 2 /nobreak >nul

REM --- 4. Frontend Logic (DEVELOPER MODE) ---
echo [System] Checking for Node modules...
if not exist "client\node_modules" (
    echo [Build] Installing frontend dependencies...
    cd /d "client" && call npm install
    cd /d "%PROJECT_DIR%"
)

REM Terminal 3: Frontend LIVE on :5173 (Vite Default)
echo [Launch] Starting Live Frontend...
start "Holo-Docs: Frontend (Live)" cmd /k "cd /d client && npm run dev"

echo.
echo === All services are running! ===
echo    Orchestrator: http://localhost:8080/api/health
echo    Vision WS:    ws://localhost:8001/ws/frames/{sessionId}
echo    Frontend:     http://localhost:5173  <-- USE THIS NEW URL
echo.
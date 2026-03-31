import { useEffect, useRef, useCallback } from 'react';

const FRAME_WIDTH = 320;
const FRAME_HEIGHT = 240;
const JPEG_QUALITY = 0.6;

/**
 * Captures webcam frames and sends them as JPEG binary over WebSocket
 * to the Vision service. Runs at ~30fps.
 */
export function useWebcamStream(sessionId: string, visionWsUrl: string) {
  const wsRef = useRef<WebSocket | null>(null);
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const rafRef = useRef<number>(0);
  const lastSendRef = useRef<number>(0);

  const start = useCallback(async () => {
    // Set up hidden video + canvas for capture
    const video = document.createElement('video');
    video.setAttribute('playsinline', '');
    video.setAttribute('autoplay', '');
    videoRef.current = video;

    const canvas = document.createElement('canvas');
    canvas.width = FRAME_WIDTH;
    canvas.height = FRAME_HEIGHT;
    canvasRef.current = canvas;

    // Request webcam
    const stream = await navigator.mediaDevices.getUserMedia({
      video: { width: FRAME_WIDTH, height: FRAME_HEIGHT, facingMode: 'user' },
    });
    video.srcObject = stream;
    await video.play();

    // Connect WS to vision service
    const url = `${visionWsUrl}/ws/frames/${sessionId}`;
    const ws = new WebSocket(url);
    ws.binaryType = 'arraybuffer';
    wsRef.current = ws;

    ws.onopen = () => {
      console.log('[webcam] WS connected to vision service');
      captureLoop();
    };

    ws.onerror = (e) => console.error('[webcam] WS error:', e);
    ws.onclose = () => console.log('[webcam] WS closed');
  }, [sessionId, visionWsUrl]);

  const captureLoop = useCallback(() => {
    const video = videoRef.current;
    const canvas = canvasRef.current;
    const ws = wsRef.current;

    if (!video || !canvas || !ws || ws.readyState !== WebSocket.OPEN) {
      rafRef.current = requestAnimationFrame(captureLoop);
      return;
    }

    // Throttle to ~30fps
    const now = performance.now();
    if (now - lastSendRef.current < 33) {
      rafRef.current = requestAnimationFrame(captureLoop);
      return;
    }
    lastSendRef.current = now;

    const ctx = canvas.getContext('2d')!;
    ctx.drawImage(video, 0, 0, FRAME_WIDTH, FRAME_HEIGHT);

    // Convert to JPEG blob and send as binary
    canvas.toBlob(
      (blob) => {
        if (blob && ws.readyState === WebSocket.OPEN) {
          blob.arrayBuffer().then((buf) => ws.send(buf));
        }
      },
      'image/jpeg',
      JPEG_QUALITY
    );

    rafRef.current = requestAnimationFrame(captureLoop);
  }, []);

  const stop = useCallback(() => {
    cancelAnimationFrame(rafRef.current);
    wsRef.current?.close();
    const video = videoRef.current;
    if (video?.srcObject) {
      (video.srcObject as MediaStream).getTracks().forEach((t) => t.stop());
    }
  }, []);

  useEffect(() => {
    return () => stop();
  }, [stop]);

  return { start, stop };
}

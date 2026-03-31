import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  base: './', // This ensures paths are relative, not absolute
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      // Proxy WS connections to the orchestrator
      '/ws/scene': {
        target: 'ws://localhost:8080',
        ws: true,
      },
    },
  },
});

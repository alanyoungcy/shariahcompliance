import react from '@vitejs/plugin-react'
import { defineConfig, loadEnv } from 'vite'

export default defineConfig(({ mode }) => {
  const environment = loadEnv(mode, process.cwd(), '')
  return {
    plugins: [react()],
    server: {
      proxy: {
        '/api': {
          target: environment.VITE_API_PROXY_TARGET ?? 'http://localhost:8000',
          changeOrigin: true,
        },
      },
    },
  }
})

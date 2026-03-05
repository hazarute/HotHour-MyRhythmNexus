import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'
import path from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [tailwindcss(), vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  },
  server: {
    proxy: {
      // Dev'de /api isteklerini backend'e yönlendir
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true
      },
      // Socket.IO WebSocket bağlantılarını yönlendir
      '/socket.io': {
        target: 'http://127.0.0.1:8000',
        ws: true,
        changeOrigin: true
      }
    }
  }
})

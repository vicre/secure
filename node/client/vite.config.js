import { defineConfig } from 'vite'

export default defineConfig({
  // keep default Vite root (index.html is in project root)
  server: {
    host: '0.0.0.0',
    port: 3000,
    strictPort: true
  }
})

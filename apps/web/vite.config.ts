import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

const repositoryRoot = decodeURIComponent(new URL('../..', import.meta.url).pathname)
  .replace(/^\/([A-Za-z]:\/)/, '$1')

export default defineConfig({
  plugins: [react()],
  server: {
    fs: { allow: [repositoryRoot] },
  },
})

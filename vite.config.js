import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'


const apiProxy = {
  target: 'http://127.0.0.1:8000',
  changeOrigin: true,
}


export default defineConfig({
  plugins: [vue()],
  css: {
    postcss: './postcss.config.js',
  },
  server: {
    proxy: {
      '/api': apiProxy
    }
  }
})

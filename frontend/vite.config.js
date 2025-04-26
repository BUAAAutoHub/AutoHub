import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import legacy from '@vitejs/plugin-legacy'
import vue2 from '@vitejs/plugin-vue2'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    vue2(),
    legacy({
      targets: ['ie >= 11'],
      additionalLegacyPolyfills: ['regenerator-runtime/runtime']
    })
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
      echarts: 'echarts/dist/echarts.js', // 支持echarts绘图
    }
  },
  server: {

    host: '0.0.0.0',
    port: 7999,
    open: false,
    proxy: {
      '/api': {
        // // target: 'http://114.116.219.29:8001',
        // target:  'http://104.208.78.33:8001/',
        //target: 'http://127.0.0.1:8001',
        target: 'http://127.0.0.1:8001/',
        changeOrigin: true,
        rewrite: path => path
      },
      '/HPImageArchive.aspx': {
        target: 'https://cn.bing.com/',
        changeOrigin: true,
        rewrite: path => path
      }
    }
  },
  preview: {
    host: '0.0.0.0',
    port: 8001,
  }
})

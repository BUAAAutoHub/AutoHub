import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import legacy from '@vitejs/plugin-legacy'
import vue2 from '@vitejs/plugin-vue2'
import path from 'node:path'

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
      yjs: path.resolve('./node_modules/yjs/dist/yjs.cjs'),
      '@': fileURLToPath(new URL('./src', import.meta.url)),
      echarts: 'echarts/dist/echarts.js', // 支持echarts绘图
    }
  },
  server: {
    // todo: 随着npm run dev打开的前端端口，port也应同步变化
    host: '10.254.47.34',
    port: 7999,
    open: false,
    historyApiFallback: true,
    proxy: {
      '/api': {
        // // target: 'http://114.116.219.29:8000',
        // target:  'http://104.208.78.33:8000/',
        //target: 'http://127.0.0.1:8000',
        target: 'http://10.254.47.34:8000',
        //target: "http://localhost:8001", // 开发环境可用
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
    host: '10.254.47.34',
    port: 8000,
  }
})

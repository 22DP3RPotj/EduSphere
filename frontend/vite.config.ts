import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default () => {
  return defineConfig({
    define: {
      __API_URL__: JSON.stringify('/graphql/'),
      __WS_URL__: JSON.stringify('localhost/ws'),
    },
    server: {
      hmr: {
        clientPort: 80,
        protocol: 'ws',
        host: 'localhost'
      },
      strictPort: true
    },
    plugins: [
      vue(),
      vueDevTools(),
    ],
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url))
      },
    },
    build: {
      minify: 'terser',
      // terserOptions: {
      //   compress: {
      //     drop_console: true,
      //     drop_debugger: true,
      //   },
      // },
      rollupOptions: {
        output: {
          manualChunks: {
            vendor: ["vue", "vue-router", "pinia"],
          },
        },
      },
      chunkSizeWarningLimit: 1600,
    },
  })
}
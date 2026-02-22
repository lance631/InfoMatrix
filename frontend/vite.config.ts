import { defineConfig } from 'vite'
import { devtools } from '@tanstack/devtools-vite'
import tsconfigPaths from 'vite-tsconfig-paths'

// @ts-ignore - TanStack Start plugin types
import { tanstackStart } from '@tanstack/react-start/plugin/vite'

import viteReact from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
// @ts-ignore - Nitro types
import { nitro } from 'nitro/vite'

const config = defineConfig({
  plugins: [
    devtools(),
    nitro({
      rollupConfig: { external: [/^@sentry\//] },
      experimental: {
        serverAssets: true,
      },
      // Disable dev server reload to prevent HMR issues
      devServer: {
        watch: false,
      },
    }),
    tsconfigPaths({ projects: ['./tsconfig.json'] }),
    tailwindcss(),
    tanstackStart(),
    viteReact(),
  ],
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
    // Improve HMR
    hmr: {
      overlay: false,
    },
    watch: {
      // Ignore certain directories to reduce HMR noise
      ignored: ['**/node_modules/**', '**/.output/**'],
    },
  },
  ssr: {
    noExternal: ['@tanstack/react-start'],
  },
  optimizeDeps: {
    exclude: ['nitro'],
  },
})

export default config

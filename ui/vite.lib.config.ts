/*
 * Configuration to build AutoArena UI as a library of components that can be imported into other projects
 */
import { resolve } from 'path';
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import dts from 'vite-plugin-dts';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react(), dts({ insertTypesEntry: true })],
  assetsInclude: ['assets/*'],
  build: {
    lib: {
      entry: resolve(__dirname, 'src/index.ts'),
      name: 'autoarena',
      fileName: 'autoarena',
    },
    rollupOptions: {
      external: ['react'],
      output: {
        globals: {
          react: 'React',
        },
      },
    },
  },
});

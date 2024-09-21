/*
 * Main build configuration for AutoArena UI static HTML/CSS/JS assets
 */
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  assetsInclude: ['assets/*'],
});

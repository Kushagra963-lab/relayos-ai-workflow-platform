import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

const repoName = process.env.GITHUB_REPOSITORY?.split('/')[1] || 'vectorshift-assessment-kushagra';
const base = process.env.GITHUB_PAGES === 'true' ? `/${repoName}/` : '/';

export default defineConfig({
  base,
  plugins: [react()],
  server: {
    port: 5173
  },
  preview: {
    port: 4173
  }
});

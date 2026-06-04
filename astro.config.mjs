import { defineConfig } from 'astro/config';
import mdx from '@astrojs/mdx';
import { fileURLToPath } from 'url';
import path from 'path';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

export default defineConfig({
  site: 'https://ericaraujo.com',
  integrations: [mdx()],
  output: 'static',
  vite: {
    resolve: {
      alias: {
        '@data': path.resolve(__dirname, './data'),
      },
    },
  },
});

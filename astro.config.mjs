import { defineConfig } from 'astro/config';
import mdx from '@astrojs/mdx';
import { rm } from 'node:fs/promises';

// Pages (and asset folders) that are still being worked on.
//
// `npm run dev` serves these normally, so you can look at them locally. They are
// stripped from the production build, so `npm run build` — and therefore the
// GitHub Pages deploy — never publishes them. Delete an entry from this list
// when the page is ready to go live, and re-add its link to the navbar.
const DRAFTS = [
  'story',    // src/pages/story.astro
  'moments',  // public/moments/ — photos used only by the story page
];

/** @type {import('astro').AstroIntegration} */
const excludeDrafts = {
  name: 'exclude-drafts',
  hooks: {
    'astro:build:done': async ({ dir, logger }) => {
      for (const name of DRAFTS) {
        await rm(new URL(`./${name}/`, dir), { recursive: true, force: true });
        await rm(new URL(`./${name}.html`, dir), { force: true });
      }
      if (DRAFTS.length) logger.warn(`draft, not published: ${DRAFTS.join(', ')}`);
    },
  },
};

export default defineConfig({
  site: 'https://ericaraujo.com',
  integrations: [mdx(), excludeDrafts],
  output: 'static',
});

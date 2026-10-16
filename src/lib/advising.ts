// ─────────────────────────────────────────────────────────────────────────────
// Academic advising: data loading for /advising and /advising/<season>/
//
// Data lives in two folders so a new semester never overwrites an old one:
//
//   data/advising/seasons/<id>.json   one per advising season (dates, booking
//                                     link, workshops, help links). The id is
//                                     "<year>-<term>", e.g. "2027-spring" is the
//                                     season in Fall 2026 that advises for
//                                     Spring 2027.
//   data/advising/catalogs/<id>.json  one per catalog year (course facts,
//                                     program maps, core table). Seasons point
//                                     at one with their `catalog` field, so two
//                                     seasons in the same academic year share it.
//
// A season with `"draft": true` is visible in `npm run dev` but left out of the
// production build entirely: no page, no link from the hub.
// ─────────────────────────────────────────────────────────────────────────────

export type Pair = [string, string];

export interface Season {
  id: string;
  term: string;
  draft?: boolean;
  catalog: string;
  updated: string;
  /** Page title and the TL;DR bullets under it (HTML allowed). */
  hero: { title: string; tldrHtml: string[] };
  booking: { url: string; label: string };
  prepare: {
    title: string;
    rule: string;
    ruleText: string;
    steps: { titleHtml: string; links: Pair[] }[];
    after: string;
  };
  dates: {
    eyebrow: string;
    registration: Pair[];
    registrationNoteHtml: string;
    events: Pair[];
    eventsNoteHtml: string;
  };
  /** Two columns of list items (HTML). */
  help: string[][];
  /** Optional, unofficial list of courses with sections next term (map tags). */
  nextTerm?: { term: string; sourceLabel: string; sourceUrl: string; checked: string; courses: string[] };
}

export interface Catalog {
  id: string;
  label: string;
  catalogUrl: string;
  sourceNote: string;
  programs: Record<string, { name: string; [k: string]: unknown }>;
  /** Optional "Minors and certificates" section. Items' html may hold links. */
  addOns?: { intro?: string; items: { for?: string; html: string }[]; moreHtml?: string };
  core: {
    requirement: string;
    isNew?: boolean;
    asks: string;
    bcs: { status: 'yes' | 'part' | 'no'; courses?: string };
    plus: { status: 'yes' | 'part' | 'no'; courses?: string };
    ds: { status: 'yes' | 'part' | 'no'; courses?: string };
  }[];
  [k: string]: unknown;
}

const seasonFiles = import.meta.glob<Season>('../../data/advising/seasons/*.json', { eager: true, import: 'default' });
const catalogFiles = import.meta.glob<Catalog>('../../data/advising/catalogs/*.json', { eager: true, import: 'default' });

// Within a year, terms run Interim → Spring → Summer → Fall.
const TERM_ORDER: Record<string, number> = { interim: 1, spring: 2, summer: 3, fall: 4 };
const sortKey = (id: string) => {
  const [year, term] = id.split('-');
  return Number(year) * 10 + (TERM_ORDER[term] ?? 0);
};

/** Seasons that should exist in this build, newest first. Drafts only in dev. */
export function getSeasons(): Season[] {
  return Object.values(seasonFiles)
    .filter((s) => !(s.draft && import.meta.env.PROD))
    .sort((a, b) => sortKey(b.id) - sortKey(a.id));
}

export function getCatalog(id: string): Catalog {
  const c = Object.values(catalogFiles).find((x) => x.id === id);
  if (!c) throw new Error(`advising: season refers to catalog "${id}", but data/advising/catalogs/${id}.json does not exist`);
  return c;
}

/** The season /advising shows: the newest one that is not a draft. */
export function getCurrentSeason(): Season | undefined {
  return getSeasons().find((s) => !s.draft);
}

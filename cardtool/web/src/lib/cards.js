// Pure card logic ported verbatim from the monolith (index.legacy.html).
// No runes here: this module holds constants and pure predicates only, so it
// stays a plain .js file that any store or component can import.

// Search fields: [key, label, getter]. The getter reads the raw card value that
// gets lowercased into card._f[key] at load time (see data.svelte.js).
export const SEARCH_FIELDS = [
  ['name', 'Name', (c) => c.name],
  ['effect', 'Effect', (c) => c.effect],
  ['cardType', 'Card type', (c) => c.cardType],
  ['kind', 'Kind', (c) => c.kind],
  ['attribute', 'Attribute', (c) => c.attribute],
  ['race', 'Race', (c) => c.race],
  ['icon', 'Icon', (c) => c.icon],
  ['level', 'Level', (c) => c.level],
  ['atk', 'ATK', (c) => c.atk],
  ['def', 'DEF', (c) => c.def],
  ['password', 'Password', (c) => c.password],
  ['pack', 'Pack', (c) => c.pack],
]

// Table columns.
export const COLS = [
  { k: 'name', label: 'Name' },
  { k: 'cardType', label: 'Type' },
  { k: 'attribute', label: 'Attr' },
  { k: 'race', label: 'Race' },
  { k: 'kind', label: 'Kind' },
  { k: 'level', label: 'Lv', num: true },
  { k: 'atk', label: 'ATK', num: true },
  { k: 'def', label: 'DEF', num: true },
  { k: 'effect', label: 'Effect' },
]

export const ATTRS = ['LIGHT', 'DARK', 'WATER', 'FIRE', 'EARTH', 'WIND', 'DIVINE']

export const KIND_ORDER = ['Normal', 'Effect', 'Fusion', 'Ritual', 'Synchro', 'Tuner', 'Toon', 'Spirit', 'Union', 'Gemini', 'Token']

export const RARITY_RANK = { 'Ultra Rare': 0, 'Super Rare': 1, Rare: 2, Common: 3 }
export const RARITY_BADGE = { Common: ['C', 'rr-C'], Rare: ['R', 'rr-R'], 'Super Rare': ['SR', 'rr-S'], 'Ultra Rare': ['UR', 'rr-U'] }

// Max rows rendered at once (cap applied in CardTable, not the results store).
export const CAP = 500

// External YGOPRODeck image URLs (unaffected by the local public/ base path).
export const imgSmall = (c) => (c.imgId ? `https://images.ygoprodeck.com/images/cards_small/${c.imgId}.jpg` : null)
export const imgFull = (c) => (c.imgId ? `https://images.ygoprodeck.com/images/cards/${c.imgId}.jpg` : null)

// Card-frame class key from card fields (drives .f-* frame vocabulary).
export const FRAME = (c) => {
  if (c.cardType === 'Spell') return 'spell'
  if (c.cardType === 'Trap') return 'trap'
  const t = c.types || []
  return t.includes('Synchro')
    ? 'synchro'
    : t.includes('Fusion')
      ? 'fusion'
      : t.includes('Ritual')
        ? 'ritual'
        : t.includes('Token')
          ? 'token'
          : t.includes('Normal')
            ? 'normal'
            : 'effect'
}

// Numeric range predicate. "" bounds mean unbounded; non-number values ("?"/null)
// are excluded once any bound is set.
export function inRange(v, lo, hi) {
  if (lo === '' && hi === '') return true
  if (typeof v !== 'number') return false
  if (lo !== '' && v < +lo) return false
  if (hi !== '' && v > +hi) return false
  return true
}

// Filter predicate. Reads filters (q + SvelteSets + range strings) and searchIn
// (per-field enable map) instead of the monolith's S / SF globals. Uses the
// precomputed lowercased card._f for the free-text AND search.
export function match(card, filters, searchIn) {
  const q = (filters.q || '').trim().toLowerCase()
  if (q) {
    let hay = ''
    for (const [k] of SEARCH_FIELDS) if (searchIn[k]) hay += card._f[k] + '\n'
    for (const w of q.split(/\s+/)) if (w && !hay.includes(w)) return false
  }
  if (filters.types.size && !filters.types.has(card.cardType)) return false
  if (filters.attrs.size && !filters.attrs.has(card.attribute)) return false
  if (filters.races.size && !filters.races.has(card.race)) return false
  if (filters.kinds.size && !card.types.some((t) => filters.kinds.has(t))) return false
  if (filters.icons.size && !filters.icons.has(card.icon)) return false
  if (!inRange(card.level, filters.lvMin, filters.lvMax)) return false
  if (!inRange(card.atk, filters.atkMin, filters.atkMax)) return false
  if (!inRange(card.def, filters.defMin, filters.defMax)) return false
  return true
}

// Sort key: null/undefined sorts as -1 for numeric columns, '' otherwise.
export const sortKey = (c, k) => {
  const v = c[k]
  return v == null ? (COLS.find((x) => x.k === k)?.num ? -1 : '') : v
}

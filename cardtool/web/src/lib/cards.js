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
  ['limit', 'Limit', (c) => c.limit],
]

// Table columns.
export const COLS = [
  { k: 'name', label: 'Name' },
  { k: 'limit', label: 'Limit' },
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

// Badge geometry per tier (rendered as SVG by LimitBadge.svelte).
export const LIMIT_STYLE = {
  Forbidden: { fill: '#e23b3b', slash: true },
  Limited: { fill: '#e8892b', text: '1', color: '#fff' },
  'Semi-Limited': { fill: '#d9b421', text: '2', color: '#20242e' },
}
// Restriction rank for the sortable Limit column; unlisted (Unlimited) cards sort last.
export const LIMIT_RANK = { Forbidden: 0, Limited: 1, 'Semi-Limited': 2 }

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

// Google-style query compiled once per keystroke (parseQuery) then tested per
// card (matchQuery). Grammar: OR-groups (split on a bare `or`/`OR`/`|`) of
// implicit-AND terms. A term is a substring atom, optionally negated with `-`
// and optionally scoped to a field (`name:dragon`, `atk:>2000`, `lv:4..8`).
// Aliases map to canonical card keys; numeric fields compare the real number.
const FIELD_MAP = {
  name: 'name', effect: 'effect', text: 'effect', desc: 'effect',
  cardtype: 'cardType', type: 'cardType', kind: 'kind',
  attribute: 'attribute', attr: 'attribute', race: 'race', icon: 'icon',
  level: 'level', lv: 'level', lvl: 'level', atk: 'atk', def: 'def',
  password: 'password', pass: 'password', pack: 'pack', limit: 'limit',
}
const NUMERIC = new Set(['level', 'atk', 'def'])
// "attr"/"lv"/"pass" are prefixes of longer aliases; longest must match first.
const FIELD_ALT = Object.keys(FIELD_MAP).sort((a, b) => b.length - a.length).join('|')
const TOKEN_RE = new RegExp(String.raw`(-?)(?:(${FIELD_ALT}):)?(?:"([^"]*)"|(\S+))`, 'gi')

// Parses a numeric field expression: ">=2000", "<1000", "2000", "4..8". Returns
// {op,n} | {lo,hi} | null (null falls back to a substring match on the field).
function parseNum(v) {
  let m
  if ((m = /^(\d+)\.\.(\d+)$/.exec(v))) return { lo: +m[1], hi: +m[2] }
  if ((m = /^(>=|<=|>|<|=)?(\d+)$/.exec(v))) return { op: m[1] || '=', n: +m[2] }
  return null
}

// Compiles a query string into { groups: Atom[][] }. Each Atom is
// { neg, field, text } or { neg, field, num }; field null = full haystack.
export function parseQuery(raw) {
  const groups = [[]]
  TOKEN_RE.lastIndex = 0
  let m
  while ((m = TOKEN_RE.exec((raw || '').toLowerCase()))) {
    const [, dash, fieldName, quoted, bare] = m
    const quotedTerm = quoted !== undefined
    const value = quotedTerm ? quoted : bare
    if (value === '') continue
    // Only bare `or`/`|` splits groups; quote them ("or") to search literally.
    if (!dash && !fieldName && !quotedTerm && (value === 'or' || value === '|')) {
      if (groups[groups.length - 1].length) groups.push([])
      continue
    }
    const neg = dash === '-'
    const cur = groups[groups.length - 1]
    if (fieldName) {
      const field = FIELD_MAP[fieldName]
      if (NUMERIC.has(field) && !quotedTerm) {
        const num = parseNum(value)
        if (num) { cur.push({ neg, field, num }); continue }
      }
      cur.push({ neg, field, text: value })
    } else {
      cur.push({ neg, field: null, text: value })
    }
  }
  return { groups: groups.filter((g) => g.length) }
}

// Tests one atom against a card. Full-text atoms hit the enabled haystack (built
// lazily via getHay); field atoms hit that one field only.
function testAtom(atom, card, getHay) {
  if (atom.field === null) return getHay().includes(atom.text)
  if (atom.num) {
    const v = card[atom.field]
    if (typeof v !== 'number') return false
    const n = atom.num
    if (n.op === undefined) return v >= n.lo && v <= n.hi
    return n.op === '>' ? v > n.n : n.op === '>=' ? v >= n.n : n.op === '<' ? v < n.n : n.op === '<=' ? v <= n.n : v === n.n
  }
  return (card._f[atom.field] || '').includes(atom.text)
}

// True if any OR-group fully matches: every positive term present, no negated
// term present. No groups (empty query) matches everything.
export function matchQuery(groups, card, searchIn) {
  if (!groups.length) return true
  let hay = null
  const getHay = () => {
    if (hay === null) {
      hay = ''
      for (const [k] of SEARCH_FIELDS) if (searchIn[k]) hay += card._f[k] + '\n'
    }
    return hay
  }
  for (const group of groups) {
    let ok = true
    for (const atom of group) {
      const hit = testAtom(atom, card, getHay)
      if (atom.neg ? hit : !hit) { ok = false; break }
    }
    if (ok) return true
  }
  return false
}

// Filter predicate. Reads filters (SvelteSets + range strings) and searchIn
// (per-field enable map). The text query is precompiled once by the caller and
// passed as `compiled`; falls back to parsing filters.q if omitted.
export function match(card, filters, searchIn, compiled, ownedSet) {
  if (ownedSet && ownedSet.size > 0 && !ownedSet.has(card.idx)) return false
  const groups = (compiled || parseQuery(filters.q)).groups
  if (!matchQuery(groups, card, searchIn)) return false
  if (filters.types.size && !filters.types.has(card.cardType)) return false
  if (filters.limits.size && !filters.limits.has(card.limit || 'Unlimited')) return false
  if (filters.attrs.size && !filters.attrs.has(card.attribute)) return false
  if (filters.races.size && !filters.races.has(card.race)) return false
  if (filters.kinds.size && !card.types.some((t) => filters.kinds.has(t))) return false
  if (filters.icons.size && !filters.icons.has(card.icon)) return false
  if (!inRange(card.level, filters.lvMin, filters.lvMax)) return false
  if (!inRange(card.atk, filters.atkMin, filters.atkMax)) return false
  if (!inRange(card.def, filters.defMin, filters.defMax)) return false
  return true
}

// Sort key: null/undefined and variable "?" stats sort as -1 for numeric columns, '' otherwise.
export const sortKey = (c, k) => {
  if (k === 'limit') return LIMIT_RANK[c.limit] ?? 3
  const v = c[k]
  if (COLS.find((x) => x.k === k)?.num) return typeof v === 'number' ? v : -1
  return v ?? ''
}

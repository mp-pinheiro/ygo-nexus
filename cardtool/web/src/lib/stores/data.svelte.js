// Loaded card DB + derived indexes/facets. The 4305-card array is $state.raw to
// avoid deep-proxying every card; the indexes/facets are plain module vars built
// once in loadDB() and never reassigned after, so they need no reactivity.
import { SEARCH_FIELDS, KIND_ORDER } from '../cards.js'

let _cards = $state.raw([])
let _loaded = $state(false)
let _error = $state(null)

// Built once in loadDB(); plain values (not runes).
let _packs = {}
let _byIdx = new Map()
let _packCards = {}
let _races = []
let _kinds = []
let _icons = []

// Getter object: you cannot export a reassigned $state binding directly, so
// reads go through getters that stay reactive for _cards / _loaded / _error.
export const data = {
  get cards() {
    return _cards
  },
  get loaded() {
    return _loaded
  },
  get error() {
    return _error
  },
  get count() {
    return _cards.length
  },
  get packs() {
    return _packs
  },
  get byIdx() {
    return _byIdx
  },
  get packCards() {
    return _packCards
  },
  get races() {
    return _races
  },
  get kinds() {
    return _kinds
  },
  get icons() {
    return _icons
  },
}

// Fetches cards.json and replicates the monolith's load-time preprocessing
// (search index, byIdx map, pack grouping, facet lists). On failure it leaves
// loaded=false and exposes an error message.
export async function loadDB() {
  try {
    const res = await fetch((import.meta.env.VITE_DATA_BASE || import.meta.env.BASE_URL) + 'cards.json')
    if (!res.ok) throw new Error(`HTTP ${res.status} loading cards.json`)
    const db = await res.json()
    const cards = db.cards || []

    // Lowercased search index per card (card._f[key]).
    cards.forEach((c) => {
      c._f = {}
      for (const [k, , get] of SEARCH_FIELDS) c._f[k] = String(get(c) ?? '').toLowerCase()
    })

    _byIdx = new Map(cards.map((c) => [c.idx, c]))
    _packs = db.packs || {}
    _packCards = {}
    cards.forEach((c) => {
      if (c.pack) (_packCards[c.pack] ||= []).push(c)
    })

    const uniq = (k) => [...new Set(cards.map((c) => c[k]).filter(Boolean))]
    _races = uniq('race').sort()
    const kindTags = new Set(cards.flatMap((c) => c.types || []))
    _kinds = KIND_ORDER.filter((t) => kindTags.has(t))
    _icons = uniq('icon').sort()

    _cards = cards
    _loaded = true
  } catch (err) {
    _error = err instanceof Error ? err.message : String(err)
    _loaded = false
  }
}

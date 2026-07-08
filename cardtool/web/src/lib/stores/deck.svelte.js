// Deck editor state: named decks (main/extra/side = arrays of card idx) persisted
// to localStorage, with banlist-aware add rules. Copy caps apply by card NAME —
// alt-arts (distinct idx, same name) share one limit — via the extracted `limit`.
import { data } from './data.svelte.js'

const STORE_KEY = 'nexus.decks'
const SCHEMA_VERSION = 1
// WC2011 has no Xyz/Link/Pendulum, so the extra deck is Fusion | Synchro.
const EXTRA_TYPES = new Set(['Fusion', 'Synchro'])
const CAP = { Forbidden: 0, Limited: 1, 'Semi-Limited': 2 }
const SECTION_CAP = { main: 60, extra: 15, side: 15 }
const SECTIONS = ['main', 'extra', 'side']
const DECK_API = '/api/decks'
let _saveTimer

export const isExtra = (card) => (card?.types || []).some((t) => EXTRA_TYPES.has(t))

export const deck = $state({ list: [], activeId: null })

function blankDeck(name = 'New Deck') {
  return { id: crypto.randomUUID(), name, main: [], extra: [], side: [] }
}

function persist() {
  const payload = JSON.stringify({ v: SCHEMA_VERSION, decks: deck.list, activeId: deck.activeId })
  try {
    localStorage.setItem(STORE_KEY, payload)
  } catch {
    // localStorage unavailable/full: rely on the KV copy.
  }
  // Debounced best-effort sync to KV (deployed); a no-op offline or in dev.
  clearTimeout(_saveTimer)
  _saveTimer = setTimeout(() => fetch(DECK_API, { method: 'PUT', body: payload }).catch(() => {}), 500)
}

function hydrate(saved) {
  if (saved?.v === SCHEMA_VERSION && Array.isArray(saved.decks) && saved.decks.length) {
    deck.list = saved.decks
    deck.activeId = saved.decks.some((d) => d.id === saved.activeId) ? saved.activeId : saved.decks[0].id
    return true
  }
  return false
}

// Hydrates instantly from localStorage, then adopts the KV copy (synced across
// devices) when reachable, seeding one empty deck if nothing is stored anywhere.
export async function loadDecks() {
  try {
    hydrate(JSON.parse(localStorage.getItem(STORE_KEY) || 'null'))
  } catch {}
  try {
    const res = await fetch(DECK_API)
    if (res.ok) hydrate(await res.json())
  } catch {}
  if (!deck.list.length) {
    const d = blankDeck()
    deck.list = [d]
    deck.activeId = d.id
  }
}

let _active = $derived(deck.list.find((d) => d.id === deck.activeId) ?? null)
export const active = {
  get deck() {
    return _active
  },
  get main() {
    return _active?.main ?? []
  },
  get extra() {
    return _active?.extra ?? []
  },
  get side() {
    return _active?.side ?? []
  },
}
export const counts = {
  get main() {
    return _active?.main.length ?? 0
  },
  get extra() {
    return _active?.extra.length ?? 0
  },
  get side() {
    return _active?.side.length ?? 0
  },
}
let _valid = $derived.by(() => {
  const d = _active
  return !!d && d.main.length >= 40 && d.main.length <= 60 && d.extra.length <= 15 && d.side.length <= 15
})
export const validity = {
  get ok() {
    return _valid
  },
}

let _stats = $derived.by(() => {
  const d = _active
  if (!d) return { monsters: 0, lo: 0, hi: 0, spells: 0, traps: 0 }
  let monsters = 0, lo = 0, hi = 0, spells = 0, traps = 0
  for (const idx of d.main) {
    const c = data.byIdx.get(idx)
    if (!c) continue
    if (c.cardType === 'Monster') { monsters++; (c.level ?? 0) >= 5 ? hi++ : lo++ }
    else if (c.cardType === 'Spell') spells++
    else if (c.cardType === 'Trap') traps++
  }
  return { monsters, lo, hi, spells, traps }
})
export const stats = {
  get monsters() { return _stats.monsters },
  get lo() { return _stats.lo },
  get hi() { return _stats.hi },
  get spells() { return _stats.spells },
  get traps() { return _stats.traps },
}

// Card name -> most-restrictive banlist tier, so same-name alt-arts share a copy
// cap. Derived from the card DB, so it fills in once loadDB() resolves.
let _nameLimit = $derived.by(() => {
  const m = new Map()
  for (const c of data.cards) {
    if (!c.limit) continue
    const cur = m.get(c.name)
    if (cur === undefined || CAP[c.limit] < CAP[cur]) m.set(c.name, c.limit)
  }
  return m
})
export const limitOf = (card) => _nameLimit.get(card.name) ?? null
export const maxCopies = (card) => {
  const tier = _nameLimit.get(card.name)
  return tier === undefined ? 3 : CAP[tier]
}
export function copiesOf(card) {
  const d = _active
  if (!d) return 0
  let n = 0
  for (const s of SECTIONS) for (const idx of d[s]) if (data.byIdx.get(idx)?.name === card.name) n++
  return n
}
export const sectionOf = (card) => (isExtra(card) ? 'extra' : 'main')

// { ok:true } or { ok:false, reason } — the reason drives the blocked-add toast.
export function canAdd(card, section = sectionOf(card)) {
  if (!_active) return { ok: false, reason: 'No deck selected' }
  if (maxCopies(card) === 0) return { ok: false, reason: `${card.name} is Forbidden` }
  if (copiesOf(card) >= maxCopies(card)) return { ok: false, reason: `Max ${maxCopies(card)} of ${card.name}` }
  if (_active[section].length >= SECTION_CAP[section]) {
    return { ok: false, reason: `${section[0].toUpperCase()}${section.slice(1)} deck is full` }
  }
  return { ok: true }
}

export function add(card, section = sectionOf(card)) {
  const v = canAdd(card, section)
  if (v.ok) {
    _active[section].push(card.idx)
    persist()
  }
  return v
}
export function removeOne(section, idx) {
  if (!_active) return
  const i = _active[section].indexOf(idx)
  if (i >= 0) {
    _active[section].splice(i, 1)
    persist()
  }
}

export function createDeck(name) {
  const d = blankDeck(name?.trim() || 'New Deck')
  deck.list.push(d)
  deck.activeId = d.id
  persist()
  return d
}
export function renameDeck(id, name) {
  const d = deck.list.find((x) => x.id === id)
  if (d && name?.trim()) {
    d.name = name.trim()
    persist()
  }
}
export function duplicateDeck(id) {
  const d = deck.list.find((x) => x.id === id)
  if (!d) return
  const copy = { id: crypto.randomUUID(), name: `${d.name} copy`, main: [...d.main], extra: [...d.extra], side: [...d.side] }
  deck.list.push(copy)
  deck.activeId = copy.id
  persist()
}
export function deleteDeck(id) {
  const i = deck.list.findIndex((x) => x.id === id)
  if (i < 0) return
  deck.list.splice(i, 1)
  if (!deck.list.length) deck.list.push(blankDeck())
  if (deck.activeId === id) deck.activeId = deck.list[0].id
  persist()
}
export function setActive(id) {
  if (deck.list.some((x) => x.id === id)) {
    deck.activeId = id
    persist()
  }
}

const TYPE_ORDER = { Monster: 0, Spell: 1, Trap: 2 }
export function grouped(section) {
  const m = new Map()
  for (const idx of active[section]) m.set(idx, (m.get(idx) ?? 0) + 1)
  return [...m]
    .map(([idx, count]) => ({ idx, count, card: data.byIdx.get(idx) }))
    .filter((r) => r.card)
    .sort((a, b) => {
      const t = TYPE_ORDER[a.card.cardType] - TYPE_ORDER[b.card.cardType]
      if (t) return t
      if (a.card.cardType === 'Monster' && (b.card.level ?? 0) !== (a.card.level ?? 0)) return (b.card.level ?? 0) - (a.card.level ?? 0)
      return a.card.name.localeCompare(b.card.name)
    })
}

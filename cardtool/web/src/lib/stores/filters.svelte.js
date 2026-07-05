// Filter + search state (replaces the monolith's S / SF globals). Facet
// selections are SvelteSet so chip toggles stay reactive (native Set is not).
import { SvelteSet } from 'svelte/reactivity'
import { SEARCH_FIELDS } from '../cards.js'

export const filters = $state({
  q: '',
  sort: 'name',
  dir: 1,
  types: new SvelteSet(),
  attrs: new SvelteSet(),
  races: new SvelteSet(),
  kinds: new SvelteSet(),
  icons: new SvelteSet(),
  lvMin: '',
  lvMax: '',
  atkMin: '',
  atkMax: '',
  defMin: '',
  defMax: '',
})

// Per-field search-in enable map; Name and Effect default on.
export const searchIn = $state(Object.fromEntries(SEARCH_FIELDS.map((f) => [f[0], f[0] === 'name' || f[0] === 'effect'])))

// Clears the five facet sets and blanks the six range strings; keeps q/sort/dir.
export function reset() {
  filters.types.clear()
  filters.attrs.clear()
  filters.races.clear()
  filters.kinds.clear()
  filters.icons.clear()
  filters.lvMin = ''
  filters.lvMax = ''
  filters.atkMin = ''
  filters.atkMax = ''
  filters.defMin = ''
  filters.defMax = ''
}

export function toggleSet(set, v) {
  set.has(v) ? set.delete(v) : set.add(v)
}

export function setAllSearchIn(v) {
  for (const [k] of SEARCH_FIELDS) searchIn[k] = v
}

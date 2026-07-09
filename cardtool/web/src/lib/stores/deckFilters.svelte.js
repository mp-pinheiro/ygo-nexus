import { SvelteSet } from 'svelte/reactivity'

export const deckFilters = $state({
  q: '',
  sort: 'type',
  dir: 1,
  types: new SvelteSet(),
})

const SORT_OPTIONS = [
  { k: 'type', label: 'Type' },
  { k: 'name', label: 'Name' },
  { k: 'level', label: 'Level' },
  { k: 'atk', label: 'ATK' },
  { k: 'def', label: 'DEF' },
  { k: 'count', label: 'Copies' },
]
export { SORT_OPTIONS }

let _hasActiveFilters = $derived(deckFilters.q !== '' || deckFilters.types.size > 0)
export const hasActiveFilters = { get value() { return _hasActiveFilters } }

export function resetDeckFilters() {
  deckFilters.q = ''
  deckFilters.sort = 'type'
  deckFilters.dir = 1
  deckFilters.types.clear()
}

export function toggleDeckSort(k) {
  if (deckFilters.sort === k) {
    deckFilters.dir *= -1
  } else {
    deckFilters.sort = k
    deckFilters.dir = 1
  }
}

// Collapsible state for the Browse-view side panels: filters (left) and deck
// (right). Panels collapse to a thin rail rather than unmounting, so the expand
// affordance stays where the panel was. Persisted to localStorage so the layout
// preference survives reloads.
const KEY = 'nexus.layout'

function load() {
  try {
    return JSON.parse(localStorage.getItem(KEY)) || {}
  } catch {
    return {}
  }
}

const saved = load()
// mFilters/mDeck are the mobile drawer flags: session-only (not persisted) so a
// phone never loads with a drawer covering the card list.
export const layout = $state({
  filters: saved.filters !== false,
  deck: saved.deck !== false,
  mFilters: false,
  mDeck: false,
})

function persist() {
  try {
    localStorage.setItem(KEY, JSON.stringify({ filters: layout.filters, deck: layout.deck }))
  } catch {
    // Private mode / storage disabled — collapse still works for the session.
  }
}

export function toggleFilters() {
  layout.filters = !layout.filters
  persist()
}

export function toggleDeck() {
  layout.deck = !layout.deck
  persist()
}

// The two drawers overlay the same viewport, so opening one closes the other.
export function openMobileFilters() {
  layout.mFilters = true
  layout.mDeck = false
}

export function openMobileDeck() {
  layout.mDeck = true
  layout.mFilters = false
}

export function closeMobilePanels() {
  layout.mFilters = false
  layout.mDeck = false
}

// Detail / zoom / pack-popover state + the Escape cascade.
// packpop shape is { idx, rect } where rect is a DOMRect from the anchor pill
// (used by PackPopover for positioning).
import { imgFull } from '../cards.js'
import { filters } from './filters.svelte.js'

export const ui = $state({ detailIdx: null, artTab: 'card', zoom: null, packpop: null })

export function showDetail(card) {
  ui.packpop = null
  ui.detailIdx = card.idx
  ui.artTab = imgFull(card) ? 'card' : 'art'
}

export function closeDetail() {
  ui.detailIdx = null
  ui.packpop = null
}

export function openZoom(url, pix) {
  ui.zoom = { url, pix }
}

export function setArtTab(mode) {
  ui.artTab = mode
}

// Single shared pack-popover close timer (monolith's one module-level packTimer,
// index.legacy.html 438-464/497-500). The pill (CardDetail) and the popover
// (PackPopover) both drive THIS timer, so entering the popover cancels the close
// scheduled when leaving the pill — without a shared timer the popover would
// dismiss ~180ms after the cursor crossed the gap into it.
let packCloseTimer
export function cancelPackClose() {
  clearTimeout(packCloseTimer)
}
export function schedulePackClose() {
  clearTimeout(packCloseTimer)
  packCloseTimer = setTimeout(() => {
    ui.packpop = null
  }, 180)
}

// Escape cascade (monolith 505-513): popover -> zoom -> detail -> clear search.
export function escape() {
  if (ui.packpop) ui.packpop = null
  else if (ui.zoom) ui.zoom = null
  else if (ui.detailIdx != null) ui.detailIdx = null
  else {
    filters.q = ''
    document.getElementById('q')?.focus()
  }
}

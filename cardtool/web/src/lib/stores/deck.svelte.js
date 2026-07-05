// PR-1 seam: deck state as arrays of card idx (main/extra/side) plus counts,
// validity, and isExtra routing. Persistence is localStorage-first, deferred to
// PR2 (reserve a save()/load() seam here).
import { data } from './data.svelte.js'

export const deck = $state({ main: [], extra: [], side: [] })

// WC2011 data has no Xyz/Link/Pendulum, so extra deck = Fusion | Synchro.
export const EXTRA_TYPES = new Set(['Fusion', 'Synchro'])

export function isExtra(card) {
  return (card.types || []).some((t) => EXTRA_TYPES.has(t))
}

let _counts = $derived({ main: deck.main.length, extra: deck.extra.length, side: deck.side.length })

export const counts = {
  get main() {
    return _counts.main
  },
  get extra() {
    return _counts.extra
  },
  get side() {
    return _counts.side
  },
}

let _valid = $derived(_counts.main >= 40 && _counts.main <= 60 && _counts.extra <= 15 && _counts.side <= 15)

export const validity = {
  get ok() {
    return _valid
  },
}

export function add(idx) {
  const card = data.byIdx.get(idx)
  ;(isExtra(card) ? deck.extra : deck.main).push(idx)
}

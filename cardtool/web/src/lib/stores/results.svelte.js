// Derived filtered + sorted card list (replaces the monolith render() 340-342).
// The 500-row CAP is applied in CardTable, not here.
import { data } from './data.svelte.js'
import { filters, searchIn } from './filters.svelte.js'
import { match, sortKey } from '../cards.js'

let _list = $derived.by(() => {
  const list = data.cards.filter((c) => match(c, filters, searchIn))
  list.sort((a, b) => {
    const x = sortKey(a, filters.sort)
    const y = sortKey(b, filters.sort)
    return (x < y ? -1 : x > y ? 1 : 0) * filters.dir
  })
  return list
})

export const results = {
  get list() {
    return _list
  },
  get count() {
    return _list.length
  },
}

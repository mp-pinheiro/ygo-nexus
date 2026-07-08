import { parseSaveFile } from '../savefile.js'
import { data } from './data.svelte.js'

const STORAGE_KEY = 'ygo-nexus-save'

let _trunkCopies = $state.raw(/** @type {Map<number,number>|null} */ (null))
let _deckGameIds = $state.raw(/** @type {number[]} */ ([]))
let _error = $state(/** @type {string|null} */ (null))

// Merges trunk ownership with deck cards once the card DB is loaded (provides
// the internal-game-id → sequential-idx mapping). Until then, returns trunk
// only. Recalculates reactively when either source changes.
let _combined = $derived.by(() => {
  if (!_trunkCopies) return null
  if (!_deckGameIds.length || !data.cards.length) return _trunkCopies
  const idToIdx = new Map()
  for (const c of data.cards) idToIdx.set(c.id, c.idx)
  const merged = new Map(_trunkCopies)
  for (const gameId of _deckGameIds) {
    const idx = idToIdx.get(gameId)
    if (idx !== undefined) merged.set(idx, (merged.get(idx) ?? 0) + 1)
  }
  return merged
})

let _total = $derived.by(() => {
  if (!_combined) return 0
  let t = 0
  for (const c of _combined.values()) t += c
  return t
})

function loadFromBytes(buf) {
  const result = parseSaveFile(buf)
  _trunkCopies = result.copies
  _deckGameIds = result.deckGameIds
}

function restoreCached() {
  try {
    const b64 = localStorage.getItem(STORAGE_KEY)
    if (!b64) return
    const bin = atob(b64)
    const buf = new Uint8Array(bin.length)
    for (let i = 0; i < bin.length; i++) buf[i] = bin.charCodeAt(i)
    loadFromBytes(buf.buffer)
  } catch { /* ignore corrupt cache */ }
}

restoreCached()

export const owned = {
  get loaded() { return _trunkCopies !== null },
  get error() { return _error },
  get count() { return _combined ? _combined.size : 0 },
  get total() { return _total },
  get set() { return _combined },
  has(idx) { return _combined ? _combined.has(idx) : false },
  copies(idx) { return _combined ? (_combined.get(idx) ?? 0) : 0 },
}

export async function importSave(file) {
  try {
    _error = null
    const buf = await file.arrayBuffer()
    loadFromBytes(buf)
    const u8 = new Uint8Array(buf)
    let b64 = ''
    for (let i = 0; i < u8.length; i++) b64 += String.fromCharCode(u8[i])
    localStorage.setItem(STORAGE_KEY, btoa(b64))
  } catch (err) {
    _error = err instanceof Error ? err.message : String(err)
    _trunkCopies = null
    _deckGameIds = []
  }
}

export function clearSave() {
  _trunkCopies = null
  _deckGameIds = []
  _error = null
  localStorage.removeItem(STORAGE_KEY)
}

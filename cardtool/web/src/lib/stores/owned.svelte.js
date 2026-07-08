import { parseSaveFile } from '../savefile.js'

let _copies = $state.raw(/** @type {Map<number,number>|null} */ (null))
let _error = $state(/** @type {string|null} */ (null))

export const owned = {
  get loaded() { return _copies !== null },
  get error() { return _error },
  get count() { return _copies ? _copies.size : 0 },
  get set() { return _copies },
  has(idx) { return _copies ? _copies.has(idx) : false },
  copies(idx) { return _copies ? (_copies.get(idx) ?? 0) : 0 },
}

export async function importSave(file) {
  try {
    _error = null
    const buf = await file.arrayBuffer()
    _copies = parseSaveFile(buf)
  } catch (err) {
    _error = err instanceof Error ? err.message : String(err)
    _copies = null
  }
}

export function clearSave() {
  _copies = null
  _error = null
}

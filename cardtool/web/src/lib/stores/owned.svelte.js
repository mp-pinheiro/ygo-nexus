import { parseSaveFile } from '../savefile.js'

let _set = $state.raw(/** @type {Set<number>|null} */ (null))
let _error = $state(/** @type {string|null} */ (null))

export const owned = {
  get set() { return _set },
  get loaded() { return _set !== null },
  get error() { return _error },
  get count() { return _set ? _set.size : 0 },
  has(idx) { return _set ? _set.has(idx) : false },
}

export async function importSave(file) {
  try {
    _error = null
    const buf = await file.arrayBuffer()
    _set = parseSaveFile(buf)
  } catch (err) {
    _error = err instanceof Error ? err.message : String(err)
    _set = null
  }
}

export function clearSave() {
  _set = null
  _error = null
}

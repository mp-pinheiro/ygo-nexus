import { parseSaveFile } from '../savefile.js'

const STORAGE_KEY = 'ygo-nexus-save'

let _copies = $state.raw(/** @type {Map<number,number>|null} */ (null))
let _error = $state(/** @type {string|null} */ (null))
let _total = $state(0)

function loadFromBytes(buf) {
  _copies = parseSaveFile(buf)
  let t = 0
  for (const c of _copies.values()) t += c
  _total = t
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
  get loaded() { return _copies !== null },
  get error() { return _error },
  get count() { return _copies ? _copies.size : 0 },
  get total() { return _total },
  get set() { return _copies },
  has(idx) { return _copies ? _copies.has(idx) : false },
  copies(idx) { return _copies ? (_copies.get(idx) ?? 0) : 0 },
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
    _copies = null
    _total = 0
  }
}

export function clearSave() {
  _copies = null
  _error = null
  _total = 0
  localStorage.removeItem(STORAGE_KEY)
}

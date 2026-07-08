const MAGIC = 'wcs2011'
const OWNERSHIP_OFFSET = 0x964C
const OWNERSHIP_END = 0xA748

// Each ownership byte encodes copies from 5 independent sources:
// bit 0 = 1 copy, bits 1-4 = 2 copies each. Max per card = 9.
function copiesFromByte(b) {
  return (b & 1)
    + ((b >> 1) & 1) * 2
    + ((b >> 2) & 1) * 2
    + ((b >> 3) & 1) * 2
    + ((b >> 4) & 1) * 2
}

// Deck slots live inside bank 1 of the save (0x8500-0xB833). Each slot is a
// fixed 220-byte record: flag + name + counts + card arrays. Card IDs are the
// game's internal 14-bit IDs (same as card_prop / banlist), NOT sequential idx.
const DECK_SLOTS_OFFSET = 0x85EC
const DECK_SLOT_SIZE = 220
const DECK_SLOT_MAX = 10
const MAIN_MAX = 60
const SIDE_MAX = 15
const EXTRA_MAX = 15

function u16(u8, off) { return u8[off] | (u8[off + 1] << 8) }
function u32(u8, off) { return (u8[off] | (u8[off + 1] << 8) | (u8[off + 2] << 16) | (u8[off + 3] << 24)) >>> 0 }

function parseDeckSlots(u8) {
  const ids = []
  for (let s = 0; s < DECK_SLOT_MAX; s++) {
    const base = DECK_SLOTS_OFFSET + s * DECK_SLOT_SIZE
    if (base + DECK_SLOT_SIZE > u8.length) break
    if (!u8[base]) continue
    const mainN = Math.min(u32(u8, base + 0x1C), MAIN_MAX)
    const sideN = Math.min(u32(u8, base + 0x20), SIDE_MAX)
    const extraN = Math.min(u32(u8, base + 0x24), EXTRA_MAX)
    for (let i = 0; i < mainN; i++) { const id = u16(u8, base + 0x28 + i * 2); if (id) ids.push(id) }
    for (let i = 0; i < sideN; i++) { const id = u16(u8, base + 0xA0 + i * 2); if (id) ids.push(id) }
    for (let i = 0; i < extraN; i++) { const id = u16(u8, base + 0xBE + i * 2); if (id) ids.push(id) }
  }
  return ids
}

export function parseSaveFile(buf) {
  const u8 = new Uint8Array(buf)
  const header = String.fromCharCode(...u8.slice(0, MAGIC.length))
  if (header !== MAGIC) throw new Error('Not a WCS2011 save file')
  if (u8.length < OWNERSHIP_END) throw new Error('Save file too small')

  const copies = new Map()
  for (let i = OWNERSHIP_OFFSET; i < OWNERSHIP_END; i++) {
    const count = copiesFromByte(u8[i])
    if (count) copies.set(i - OWNERSHIP_OFFSET, count)
  }

  const deckGameIds = parseDeckSlots(u8)
  return { copies, deckGameIds }
}

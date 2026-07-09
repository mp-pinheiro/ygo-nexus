const MAGIC = 'wcs2011'

// Card ownership: 4-bit packed array in bank 1, one nibble per sequential
// card index (low nibble = even index). Value = total copies owned across
// trunk + decks + side, capped at 9 by the game. Entry 0 is the dummy row
// before card idx 1. A mirror of the array lives in bank 2 at 0xC13E.
// Verified against in-game trunk counts (see testdata/fruta.sav).
const TRUNK_OFFSET = 0x8E06
const TRUNK_ENTRIES = 4306
const TRUNK_END = TRUNK_OFFSET + Math.ceil(TRUNK_ENTRIES / 2)

export function parseSaveFile(buf) {
  const u8 = new Uint8Array(buf)
  const header = String.fromCharCode(...u8.slice(0, MAGIC.length))
  if (header !== MAGIC) throw new Error('Not a WCS2011 save file')
  if (u8.length < TRUNK_END) throw new Error('Save file too small')

  const copies = new Map()
  for (let idx = 1; idx < TRUNK_ENTRIES; idx++) {
    const b = u8[TRUNK_OFFSET + (idx >> 1)]
    const count = idx & 1 ? b >> 4 : b & 0xF
    if (count) copies.set(idx, count)
  }
  return { copies }
}

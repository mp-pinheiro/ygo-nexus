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
  return copies
}

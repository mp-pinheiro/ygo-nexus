const MAGIC = 'wcs2011'
const OWNERSHIP_OFFSET = 0x964C
const OWNERSHIP_END = 0xA748
const COPY_MASK = 0x07

export function parseSaveFile(buf) {
  const u8 = new Uint8Array(buf)
  const header = String.fromCharCode(...u8.slice(0, MAGIC.length))
  if (header !== MAGIC) throw new Error('Not a WCS2011 save file')
  if (u8.length < OWNERSHIP_END) throw new Error('Save file too small')

  const copies = new Map()
  for (let i = OWNERSHIP_OFFSET; i < OWNERSHIP_END; i++) {
    const count = u8[i] & COPY_MASK
    if (count) copies.set(i - OWNERSHIP_OFFSET, count)
  }
  return copies
}

const MAGIC = 'wcs2011'
const OWNERSHIP_OFFSET = 0x964C
const CARD_COUNT = 4306
const COPY_MASK = 0x07

export function parseSaveFile(buf) {
  const u8 = new Uint8Array(buf)
  const header = String.fromCharCode(...u8.slice(0, MAGIC.length))
  if (header !== MAGIC) throw new Error('Not a WCS2011 save file')
  if (u8.length < OWNERSHIP_OFFSET + CARD_COUNT) throw new Error('Save file too small')

  const owned = new Set()
  for (let i = 0; i < CARD_COUNT; i++) {
    if (u8[OWNERSHIP_OFFSET + i] & COPY_MASK) owned.add(i)
  }
  return owned
}

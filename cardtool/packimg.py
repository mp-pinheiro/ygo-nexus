#!/usr/bin/env python3
"""Decode Nitro "NTBG" tile images to Pillow images.

Two producers share this format:
  - pack box art (`l_pack<N>.lz5bg` in pack.pac): LZ11-compressed, 8bpp.
  - card art (`card_5bg64x64.bin` blocks in card.pac): uncompressed, 4bpp with a
    per-tile palette bank in the tilemap's high nibble.

Container: a PALT section (BGR555 palette) + a BGDT section whose 20-byte header
gives the size in 8x8 tiles and the char-data size, followed by a tilemap then the
tile data. Palette index 0 is transparent.
"""
import struct

from PIL import Image


def lz11(data):
    size = data[1] | data[2] << 8 | data[3] << 16
    out = bytearray()
    i = 4
    while len(out) < size:
        flags = data[i]; i += 1
        for b in range(8):
            if len(out) >= size:
                break
            if flags & (0x80 >> b):
                ind = data[i] >> 4
                if ind == 0:
                    cnt = (data[i] << 4 | data[i + 1] >> 4) + 0x11
                    disp = (data[i + 1] & 0xF) << 8 | data[i + 2]; i += 3
                elif ind == 1:
                    cnt = ((data[i] & 0xF) << 12 | data[i + 1] << 4 | data[i + 2] >> 4) + 0x111
                    disp = (data[i + 2] & 0xF) << 8 | data[i + 3]; i += 4
                else:
                    cnt = ind + 1
                    disp = (data[i] & 0xF) << 8 | data[i + 1]; i += 2
                for _ in range(cnt):
                    out.append(out[len(out) - disp - 1])
            else:
                out.append(data[i]); i += 1
    return bytes(out)


def _bgr555(c):
    r, g, b = c & 0x1F, (c >> 5) & 0x1F, (c >> 10) & 0x1F
    return (r << 3 | r >> 2, g << 3 | g >> 2, b << 3 | b >> 2)


def _render(d):
    sections = {}
    off = 0x10
    for _ in range(struct.unpack_from('<H', d, 0x0E)[0]):
        sections[d[off:off + 4].decode('latin1')] = off
        off += struct.unpack_from('<I', d, off + 4)[0]
    if 'PALT' not in sections or 'BGDT' not in sections:
        return None
    po = sections['PALT']
    ncol = (struct.unpack_from('<I', d, po + 4)[0] - 12) // 2
    pal = [_bgr555(struct.unpack_from('<H', d, po + 0xC + 2 * k)[0]) for k in range(ncol)]
    bo = sections['BGDT']
    w, h = struct.unpack_from('<HH', d, bo + 8 + 8)
    char_size = struct.unpack_from('<I', d, bo + 8 + 16)[0]
    tilemap, char = bo + 8 + 20, bo + 8 + 20 + w * h * 2
    four = w * h and char_size // (w * h) == 32
    img = Image.new('RGBA', (w * 8, h * 8))
    px = img.load()
    for row in range(h):
        for col in range(w):
            ent = struct.unpack_from('<H', d, tilemap + 2 * (row * w + col))[0]
            tile, hf, vf, bank = ent & 0x3FF, ent & 0x400, ent & 0x800, (ent >> 12) & 0xF
            base = char + tile * (32 if four else 64)
            for ty in range(8):
                for tx in range(8):
                    if four:
                        byte = d[base + ty * 4 + tx // 2]
                        idx = (byte >> 4) if (tx & 1) else (byte & 0xF)
                        ci = bank * 16 + idx
                    else:
                        idx = ci = d[base + ty * 8 + tx]
                    sx = 7 - tx if hf else tx
                    sy = 7 - ty if vf else ty
                    px[col * 8 + sx, row * 8 + sy] = (*pal[ci], 0 if idx == 0 else 255)
    return img


def decode(raw):
    """Decode an LZ11-compressed .lz5bg (pack art)."""
    return _render(lz11(raw))


def decode_ntbg(d):
    """Decode an uncompressed NTBG blob (card art)."""
    return _render(d)

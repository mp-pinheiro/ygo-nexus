#!/usr/bin/env python3
"""Decode a pack box-art image (`l_pack<N>.lz5bg` in pack.pac) to a Pillow image.

The file is LZ11-compressed; the payload is a Nitro "NTBG" container of a PALT
(256-color BGR555 palette) section plus a BGDT section: a 20-byte header giving
the size in 8x8 tiles, an identity tilemap, then 8bpp tile data. Palette index 0
is treated as transparent.
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


def decode(raw):
    d = lz11(raw)
    sections = {}
    off, n = 0x10, struct.unpack_from('<H', d, 0x0E)[0]
    for _ in range(n):
        mag = d[off:off + 4].decode('latin1')
        sections[mag] = off
        off += struct.unpack_from('<I', d, off + 4)[0]
    if 'PALT' not in sections or 'BGDT' not in sections:
        return None
    po = sections['PALT']
    pal = [_bgr555(struct.unpack_from('<H', d, po + 0xC + 2 * k)[0]) for k in range(256)]
    bo = sections['BGDT']
    w, h = struct.unpack_from('<HH', d, bo + 8 + 8)      # size in 8x8 tiles
    tilemap, char = bo + 8 + 20, bo + 8 + 20 + w * h * 2
    img = Image.new('RGBA', (w * 8, h * 8))
    px = img.load()
    for row in range(h):
        for col in range(w):
            ent = struct.unpack_from('<H', d, tilemap + 2 * (row * w + col))[0]
            tile, hf, vf = ent & 0x3FF, ent & 0x400, ent & 0x800
            base = char + tile * 64
            for ty in range(8):
                for tx in range(8):
                    idx = d[base + ty * 8 + tx]
                    sx = 7 - tx if hf else tx
                    sy = 7 - ty if vf else ty
                    px[col * 8 + sx, row * 8 + sy] = (*pal[idx], 0 if idx == 0 else 255)
    return img

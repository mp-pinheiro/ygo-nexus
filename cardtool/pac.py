#!/usr/bin/env python3
"""Konami WC-series .pac archive (un)packer.

Layout (ported from YgoNdsRandomizer's PacData):
  [0 .. nameEnd)        ASCII filename table; entries are [lenByte][flagByte][name],
                        where lenByte is in 0x0A..0x18 and doubles as the separator.
                        nameEnd = offset of the first 0xFFFF marker, rounded down to 16.
  [nameEnd .. tableEnd) 0xFFFF padding + an 8-byte-per-file record table.
                        Each record: u32 addr (LE), u32 size (LE). First record and
                        any size==0 record are skipped. Table ends at the first
                        all-zero 16-byte line.
  [dataBegin .. ]       file blobs; a file lives at dataBegin+addr for size bytes.
                        dataBegin = tableEnd advanced past zero lines (16-byte steps).
"""
import struct

LINE_BREAK = set(range(0x0A, 0x19))  # 0x0A..0x18, name-length bytes / separators


def unpack(data: bytes) -> dict[str, bytes]:
    """Return {filename: blob} for a .pac archive."""
    # 1. locate 0xFFFF marker, round down to 16 -> end of ASCII name block
    name_end = None
    for i in range(0, len(data) - 1, 2):
        if data[i] == 0xFF and data[i + 1] == 0xFF:
            name_end = i - (i % 16)
            break
    if name_end is None:
        raise ValueError("no 0xFFFF marker; not a pac archive")

    names = _read_names(data[:name_end])

    # 2. record table: from name_end, 16-byte lines until first all-zero line
    i = name_end
    while i < len(data) and struct.unpack_from('<Q', data, i)[0] != 0:
        i += 16
    table = data[name_end:i]

    # 3. skip zero lines -> start of file data
    while i < len(data) and struct.unpack_from('<Q', data, i)[0] == 0:
        i += 16
    data_begin = i

    # 4. parse 8-byte records, skipping the first record and size==0 records
    files = []
    for off in range(8, len(table), 8):
        if off + 8 > len(table):
            break
        addr, size = struct.unpack_from('<II', table, off)
        if size != 0:
            files.append((data_begin + addr, size))

    if len(names) != len(files):
        raise ValueError(f"name/record mismatch: {len(names)} names vs {len(files)} records")

    out = {}
    for name, (addr, size) in zip(names, files):
        out[name] = data[addr:addr + size]
    return out


def _read_names(block: bytes) -> list[str]:
    words = []
    begin = 0
    i = 0
    n = len(block)
    while i < n:
        if block[i] in LINE_BREAK:
            words.append(block[begin:i])
            begin = i + 2
            i += 2
            continue
        i += 1
    # trailing word (trim zero padding like the reference impl)
    final = n - 1
    while final - 3 >= 0 and block[final - 3] == 0x00:
        final -= 1
    if begin < final:
        words.append(block[begin:final])
    return [w.decode('latin1').strip() for w in words if b'.' in w]


if __name__ == '__main__':
    import sys
    files = unpack(open(sys.argv[1], 'rb').read())
    print(f"{len(files)} files:")
    for name, blob in files.items():
        print(f"  {name:24s} {len(blob):>10,} bytes")

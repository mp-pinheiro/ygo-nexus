#!/usr/bin/env python3
"""Map ARM9 + overlay RAM ranges for a WC2011 NDS image and locate words/patterns.

Builds a list of memory segments (static ARM9 autoload sections + every overlay),
each with its RAM base, so any 0x02xxxxxx RAM address can be resolved to the
module(s) that cover it. Used to sanity-check guard values and relocate hook sites.
"""
import sys
import struct
import ndspy.rom


class Seg:
    __slots__ = ("name", "ram", "data", "kind", "ovid", "fileID")

    def __init__(self, name, ram, data, kind, ovid=None, fileID=None):
        self.name = name
        self.ram = ram
        self.data = data
        self.kind = kind          # 'arm9' or 'overlay'
        self.ovid = ovid
        self.fileID = fileID

    @property
    def end(self):
        return self.ram + len(self.data)

    def covers(self, addr):
        return self.ram <= addr < self.end

    def word(self, addr):
        off = addr - self.ram
        return struct.unpack_from("<I", self.data, off)[0]


def load_segments(path):
    rom = ndspy.rom.NintendoDSRom.fromFile(path)
    segs = []
    a9 = rom.loadArm9()
    for i, s in enumerate(a9.sections):
        segs.append(Seg(f"arm9.sec{i}", s.ramAddress, bytes(s.data), "arm9"))
    ovs = rom.loadArm9Overlays()
    for i in sorted(ovs):
        o = ovs[i]
        segs.append(Seg(f"ov{i:02d}", o.ramAddress, bytes(o.data), "overlay",
                        ovid=i, fileID=o.fileID))
    return rom, segs


def covering(segs, addr):
    return [s for s in segs if s.covers(addr)]


def find_pattern(segs, pat):
    hits = []
    for s in segs:
        start = 0
        while True:
            j = s.data.find(pat, start)
            if j < 0:
                break
            hits.append((s, j, s.ram + j))
            start = j + 1
    return hits


def main():
    path = sys.argv[1]
    targets = [
        (0x02182690, 0x05897060),   # DP multiplier guard
        (0x0216B1C8, 0xEA0000B9),   # Save Anywhere guard 1
        (0x0216C1C8, 0x0A00000E),   # Save Anywhere guard 2
        (0x02198408, None),         # Save Anywhere called-function ptr (value unknown)
    ]
    rom, segs = load_segments(path)
    print(f"==== {path} ====")
    print("-- segment map --")
    for s in segs:
        print(f"  {s.name:10s} ram=0x{s.ram:08X}..0x{s.end:08X} "
              f"len=0x{len(s.data):X} fileID={s.fileID}")
    print("-- target coverage (word value at each addr in every covering module) --")
    for addr, expect in targets:
        cov = covering(segs, addr)
        es = f" expect=0x{expect:08X}" if expect is not None else ""
        print(f"  addr 0x{addr:08X}{es}:")
        if not cov:
            print("      (no module covers this address)")
        for s in cov:
            w = s.word(addr)
            mark = ""
            if expect is not None:
                mark = "  <== MATCH" if w == expect else "  (mismatch)"
            print(f"      {s.name:10s} -> 0x{w:08X}{mark}")
    print("-- pattern search for guard values (LE) across all modules --")
    for val in (0x05897060, 0xEA0000B9, 0x0A00000E):
        pat = struct.pack("<I", val)
        hits = find_pattern(segs, pat)
        print(f"  value 0x{val:08X} ({pat.hex()}): {len(hits)} hit(s)")
        for s, off, ram in hits:
            print(f"      {s.name:10s} fileoff=0x{off:06X} ram=0x{ram:08X}")


if __name__ == "__main__":
    main()

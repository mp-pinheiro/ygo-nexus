#!/usr/bin/env python3
"""Disassemble hook sites (base vs hack), the Save-Anywhere payload, and the
80 differing ARM9 bytes, to confirm whether the cheat targets moved/changed."""
import struct
from capstone import Cs, CS_ARCH_ARM, CS_MODE_ARM
from analyze import load_segments, covering

MD = Cs(CS_ARCH_ARM, CS_MODE_ARM)

rom_b, segs_b = load_segments('roms/base.nds')
rom_h, segs_h = load_segments('roms/hack.nds')


def seg_for(segs, addr, prefer):
    cov = covering(segs, addr)
    for s in cov:
        if s.name == prefer:
            return s
    return cov[0] if cov else None


def disasm_range(segs, name, start, end, prefer):
    s = seg_for(segs, start, prefer)
    off = start - s.ram
    code = s.data[off:off + (end - start)]
    out = []
    for ins in MD.disasm(code, start):
        raw = struct.unpack_from('<I', s.data, ins.address - s.ram)[0]
        out.append(f"    0x{ins.address:08X}: {raw:08X}  {ins.mnemonic} {ins.op_str}")
    return s.name, out


def compare_site(label, start, end, prefer):
    print(f"\n=== {label}  [0x{start:08X}..0x{end:08X}] in {prefer} ===")
    nb, ob = disasm_range(segs_b, 'base', start, end, prefer)
    nh, oh = disasm_range(segs_h, 'hack', start, end, prefer)
    print(f"  -- BASE ({nb}) --")
    for l in ob: print(l)
    print(f"  -- HACK ({nh}) --")
    for l in oh: print(l)
    print(f"  >>> identical disassembly: {ob == oh}")


# 1) DP multiplier hook site (ov03)
compare_site("DP multiplier hook (guard@0x02182690, patch@0x02182694)",
             0x02182680, 0x021826A4, 'ov03')

# 2) Save Anywhere hook sites (ov31)
compare_site("Save Anywhere guard1 @0x0216B1C8", 0x0216B1B4, 0x0216B1DC, 'ov31')
compare_site("Save Anywhere guard2/hook @0x0216C1C8", 0x0216C1B4, 0x0216C1DC, 'ov31')

# 3) Save Anywhere BL target inside payload -> 0x02165F58 (computed)
compare_site("Save Anywhere payload BL target @0x02165F58", 0x02165F40, 0x02165F80, 'ov31')

# 4) Disassemble the Save-Anywhere payload (assembled at 0x02000100)
print("\n=== Save Anywhere payload (loaded to 0x02000100) ===")
payload = [0xE3100004,0x0A05B03F,0xE92D000F,0xE3A00B02,0xE59F1020,0xE5911000,
           0xE2811004,0xE3A02C1A,0xE2822020,0xE3A03801,0xE2433001,0xEB059589,
           0xE8BD000F,0xEA05B033]
blob = b''.join(struct.pack('<I', w) for w in payload)
for ins in MD.disasm(blob, 0x02000100):
    raw = struct.unpack_from('<I', blob, ins.address - 0x02000100)[0]
    print(f"    0x{ins.address:08X}: {raw:08X}  {ins.mnemonic} {ins.op_str}")
# pointer word that the payload reads
print("    0x02000138: 02198408  (.word  pointer read by ldr r1,[pc,#0x20])")

# 5) Locate + disassemble the 80 differing ARM9 bytes (sec0)
print("\n=== ARM9 sec0 differing regions (base vs hack) ===")
sb = seg_for(segs_b, 0x02000000, 'arm9.sec0')
sh = seg_for(segs_h, 0x02000000, 'arm9.sec0')
db, dh = sb.data, sh.data
# group differing offsets into contiguous runs (merge gaps < 16 bytes)
diffs = [i for i in range(min(len(db), len(dh))) if db[i] != dh[i]]
runs = []
for i in diffs:
    if runs and i - runs[-1][1] <= 16:
        runs[-1][1] = i
    else:
        runs.append([i, i])
print(f"  total differing bytes: {len(diffs)} in {len(runs)} region(s)")
for a, bb in runs:
    ra = sb.ram + (a & ~3)
    end = sb.ram + ((bb + 4) | 3) + 1
    print(f"\n  -- region ram 0x{ra:08X}..0x{end:08X} --")
    n = end - ra
    cb = db[ra - sb.ram: ra - sb.ram + n]
    ch = dh[ra - sb.ram: ra - sb.ram + n]
    bl = {i.address: (struct.unpack_from('<I', cb, i.address-ra)[0], i.mnemonic, i.op_str) for i in MD.disasm(cb, ra)}
    hl = {i.address: (struct.unpack_from('<I', ch, i.address-ra)[0], i.mnemonic, i.op_str) for i in MD.disasm(ch, ra)}
    for addr in sorted(set(bl) | set(hl)):
        bw = f"{bl[addr][0]:08X} {bl[addr][1]} {bl[addr][2]}" if addr in bl else "----"
        hw = f"{hl[addr][0]:08X} {hl[addr][1]} {hl[addr][2]}" if addr in hl else "----"
        mark = "" if (addr in bl and addr in hl and bl[addr][0]==hl[addr][0]) else "   <-- CHANGED"
        print(f"    0x{addr:08X}:  base[{bw:36s}]  hack[{hw:36s}]{mark}")

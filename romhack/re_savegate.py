#!/usr/bin/env python3
"""Hunt the native save trigger / gate. Build a cross-overlay map, disassemble
the command-0x800 function, and find BL callers of key addresses."""
import struct
import ndspy.rom
from capstone import Cs, CS_ARCH_ARM, CS_MODE_ARM
MD = Cs(CS_ARCH_ARM, CS_MODE_ARM)

rom = ndspy.rom.NintendoDSRom.fromFile('roms/hack.nds')
a9 = rom.loadArm9()
segs = [('arm9', a9.sections[0].ramAddress, bytes(a9.sections[0].data))]
ovd = rom.loadArm9Overlays()
for i in sorted(ovd):
    o = ovd[i]
    segs.append((f'ov{i:02d}', o.ramAddress, bytes(o.data)))

def seg_of(addr):
    for nm, r, d in segs:
        if r <= addr < r + len(d):
            return nm, r, d
    return None

def W(addr):
    s = seg_of(addr)
    return struct.unpack_from('<I', s[2], addr - s[1])[0] if s else None

def bl_target(addr, w):
    if (w & 0x0E000000) != 0x0A000000:  # B/BL family (cond any)
        return None
    link = (w >> 24) & 1
    imm = w & 0xFFFFFF
    if imm & 0x800000:
        imm -= 0x1000000
    return (addr + 8 + (imm << 2)) & 0xFFFFFFFF, link

def find_bl_callers(target):
    """All B/BL across all segs whose target == `target`."""
    hits = []
    for nm, r, d in segs:
        for off in range(0, len(d) - 3, 4):
            w = struct.unpack_from('<I', d, off)[0]
            t = bl_target(r + off, w)
            if t and t[0] == target:
                hits.append((nm, r + off, 'bl' if t[1] else 'b'))
    return hits

def dis(start, n, lbl):
    s = seg_of(start)
    if not s:
        print(f"  {lbl}: 0x{start:08X} not in any module"); return
    nm, r, d = s
    o = start - r
    print(f"=== {lbl}  ({nm}) 0x{start:08X} ===")
    for ins in MD.disasm(d[o:o + n], start):
        note = ""
        if ins.mnemonic == 'ldr' and '[pc' in ins.op_str:
            try:
                imm = int(ins.op_str.split('#')[1].rstrip(']'), 16)
                p = ins.address + 8 + imm
                v = W(p)
                if v is not None:
                    note = f"   ; =0x{v:08X}"
            except Exception:
                pass
        print(f"  0x{ins.address:08X}: {struct.unpack_from('<I', d, ins.address - r)[0]:08X}  {ins.mnemonic} {ins.op_str}{note}")

# 1) what command 0x800 actually does
dis(0x21645b8, 0x80, "command 0x800 function 0x21645b8")

# 2) who calls that function (native save path?)
print("\n=== BL/B callers of 0x21645b8 (cmd-0x800 fn) ===")
for nm, a, k in find_bl_callers(0x21645b8):
    print(f"  {k} from {nm} 0x{a:08X}")

# 3) who calls the dispatcher 0x02165758
print("\n=== BL/B callers of dispatcher 0x02165758 ===")
c = find_bl_callers(0x02165758)
print(f"  {len(c)} caller(s)")
for nm, a, k in c[:40]:
    print(f"  {k} from {nm} 0x{a:08X}")

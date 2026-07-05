#!/usr/bin/env python3
"""Find who enqueues the save command (0x800) into the command queue.
Queue ptr global = 0x02198408, active flag = 0x021983F8. Search every module
for references to these globals and for stores/uses of command id 0x800."""
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

QUEUE_PTR = 0x02198408
QUEUE_FLAG = 0x021983F8

def find_word(val):
    hits = []
    for nm, r, d in segs:
        off = 0
        while True:
            j = d.find(struct.pack('<I', val), off)
            if j < 0:
                break
            if j % 4 == 0:
                hits.append((nm, r, r + j))
            off = j + 1
    return hits

# 1) every module that references the queue globals (as literal pool constants)
for val, label in ((QUEUE_PTR, 'QUEUE_PTR 0x02198408'), (QUEUE_FLAG, 'FLAG 0x021983F8')):
    print(f"=== literal references to {label} ===")
    for nm, base, addr in find_word(val):
        print(f"  {nm}: literal@0x{addr:08X}")
    print()

# 2) within each referencing module, find the LDR that loads that literal and
#    disassemble a window to classify reader (processor) vs writer (enqueue)
def windows_using(val, before=10, after=20):
    out = []
    for nm, base, d in [(n, b, dd) for (n, b, dd) in segs]:
        for off in range(0, len(d) - 3, 4):
            w = struct.unpack_from('<I', d, off)[0]
            ins = next(MD.disasm(struct.pack('<I', w), base + off), None)
            if ins and ins.mnemonic == 'ldr' and '[pc' in ins.op_str:
                try:
                    imm = int(ins.op_str.split('#')[1].rstrip(']'), 16)
                    p = base + off + 8 + imm
                    if base <= p < base + len(d) and struct.unpack_from('<I', d, p - base)[0] == val:
                        out.append((nm, base, d, base + off))
                except Exception:
                    pass
    return out

print("=== code sites that LOAD the queue pointer 0x02198408 ===")
for nm, base, d, addr in windows_using(QUEUE_PTR):
    print(f"\n-- {nm} @0x{addr:08X} --")
    o = addr - base - 6 * 4
    for ins in MD.disasm(d[max(0, o):o + 26 * 4], base + max(0, o)):
        mark = " <<<" if ins.address == addr else ""
        print(f"   0x{ins.address:08X}: {ins.mnemonic} {ins.op_str}{mark}")

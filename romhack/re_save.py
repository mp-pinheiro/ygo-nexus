#!/usr/bin/env python3
"""Reverse-engineer the Save-Anywhere hook region in ov31. Resolve PC-relative
literals, find the enclosing function, and inspect the payload's call target."""
import struct
import ndspy.rom
from capstone import Cs, CS_ARCH_ARM, CS_MODE_ARM
MD = Cs(CS_ARCH_ARM, CS_MODE_ARM)

ov = ndspy.rom.NintendoDSRom.fromFile('roms/hack.nds').loadArm9Overlays()[31]
base = ov.ramAddress
data = bytes(ov.data)

def w(addr):
    return struct.unpack_from('<I', data, addr - base)[0]

def dis(start, end, resolve_ldr=True):
    off = start - base
    for ins in MD.disasm(data[off:off + (end - start)], start):
        raw = w(ins.address)
        note = ""
        # resolve  ldr rX, [pc, #imm]
        if resolve_ldr and ins.mnemonic == 'ldr' and '[pc' in ins.op_str:
            imm = int(ins.op_str.split('#')[1].rstrip(']'), 16)
            ptr = ins.address + 8 + imm
            if base <= ptr < base + len(data):
                note = f"   ; ={w(ptr):08X} (literal@0x{ptr:08X})"
        print(f"  0x{ins.address:08X}: {raw:08X}  {ins.mnemonic} {ins.op_str}{note}")

# find function start: scan backwards for a push {... lr} (E92Dxxxx with bit14 set)
print("=== scan back for function prologue before 0x0216C1B4 ===")
a = 0x0216C1B4
start = None
for addr in range(0x0216C1B4, 0x0216BE00, -4):
    v = w(addr)
    if (v & 0x0FFF0000) == 0x092D0000 and (v & 0x4000):  # stmfd sp!{...,lr}
        start = addr
        print(f"  function start ~0x{addr:08X}: {v:08X}")
        break
print()

print("=== hook function body ===")
dis(start if start else 0x0216C190, 0x0216C228)

print("\n=== literal pool 0x0216C290..0x0216C2B0 ===")
for addr in range(0x0216C28C, 0x0216C2B4, 4):
    print(f"  0x{addr:08X}: {w(addr):08X}")

print("\n=== payload call target 0x02165758 (first part) ===")
dis(0x02165758, 0x021657A0)

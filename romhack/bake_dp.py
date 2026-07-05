#!/usr/bin/env python3
"""Bake the Total DP Multiplier into hack.nds as a single guard-verified in-place
instruction patch in ov3 (RAM 0x02182694), producing hack_dp<N>x.nds.

This is exactly how hack_dp16x.nds was made; only the shift amount changes. N must
be a power of two in 2..128 (matches the AR codes in base.cht 'Total DP Multiplier',
cheat14..cheat20). The patched word is

    addne r0, r0, r7, lsl #log2(N)      == r0 += r7 * N

i.e. 0x10800007 | (log2(N) << 7), byte-identical to what the AR code writes.

    ./.venv/bin/python bake_dp.py [N=4] [out=hack_dp<N>x.nds]
"""
import sys
import struct
import ndspy.rom
import ndspy.code

DP_OV, DP_OFF = 3, 0x40EB4               # ov3, RAM 0x02182694
GUARD, STOCK = 0x05897060, 0x10800007    # word@0x02182690 , stock word@0x02182694


def opcode(mult):
    if mult < 2 or mult > 128 or (mult & (mult - 1)):
        raise ValueError(f"multiplier must be a power of two in 2..128, got {mult}")
    return STOCK | ((mult.bit_length() - 1) << 7)


def bake(mult, out):
    val = opcode(mult)
    rom = ndspy.rom.NintendoDSRom.fromFile('roms/hack.nds')
    ovs = rom.loadArm9Overlays()
    ov3 = ovs[DP_OV]
    d = bytearray(ov3.data)
    assert struct.unpack_from('<I', d, DP_OFF - 4)[0] == GUARD, "guard word mismatch"
    assert struct.unpack_from('<I', d, DP_OFF)[0] == STOCK, "DP site is not stock"
    struct.pack_into('<I', d, DP_OFF, val)
    ov3.data = bytes(d)
    rom.files[ov3.fileID] = ov3.save(compress=True)
    rom.arm9OverlayTable = ndspy.code.saveOverlayTable(ovs)
    rom.saveToFile(out)
    return val


def verify(out, expect):
    r = ndspy.rom.NintendoDSRom.fromFile(out)
    ov3 = r.loadArm9Overlays()[DP_OV]
    guard = struct.unpack_from('<I', ov3.data, DP_OFF - 4)[0]
    got = struct.unpack_from('<I', ov3.data, DP_OFF)[0]
    ok = True
    try:
        r.loadArm9()
        for i in sorted(r.loadArm9Overlays()):
            _ = r.loadArm9Overlays()[i].data
    except Exception as e:
        ok = False
        print("  integrity ERROR:", e)
    print(f"[{out}] guard=0x{guard:08X} dp@0x02182694=0x{got:08X} "
          f"expect=0x{expect:08X}  {'OK' if got == expect and guard == GUARD else 'FAIL'}  "
          f"integrity={'OK' if ok else 'BROKEN'}")


if __name__ == '__main__':
    mult = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    out = sys.argv[2] if len(sys.argv) > 2 else f'roms/hack_dp{mult}x.nds'
    val = bake(mult, out)
    print(f"baked {mult}x -> 0x{val:08X} into {out}")
    verify(out, val)

#!/usr/bin/env python3
"""Report the DP-multiplier instruction (ov3 file-offset 0x40EB4 / RAM 0x02182694)
in every ROM, decoded, so we know exactly what each baked image contains."""
import struct
import glob
import ndspy.rom
from capstone import Cs, CS_ARCH_ARM, CS_MODE_ARM
MD = Cs(CS_ARCH_ARM, CS_MODE_ARM)

DP_OV, DP_OFF, GUARD_OFF = 3, 0x40EB4, 0x40EB0
KNOWN = {
    0x10800007: "stock (r7*1, unpatched)",
    0x10800087: "2x  (lsl #1)",
    0x10800107: "4x  (lsl #2)",
    0x10800187: "8x  (lsl #3)",
    0x10800207: "16x (lsl #4)",
    0x10800287: "32x (lsl #5)",
    0x10800307: "64x (lsl #6)",
    0x10800387: "128x (lsl #7)",
}

for path in sorted(glob.glob("roms/*.nds")):
    try:
        ov = ndspy.rom.NintendoDSRom.fromFile(path).loadArm9Overlays()[DP_OV]
        guard = struct.unpack_from('<I', ov.data, GUARD_OFF)[0]
        word = struct.unpack_from('<I', ov.data, DP_OFF)[0]
        ins = next(MD.disasm(struct.pack('<I', word), 0x02182694), None)
        txt = f"{ins.mnemonic} {ins.op_str}" if ins else "??"
        print(f"{path:20s} guard=0x{guard:08X} dp=0x{word:08X}  {txt:24s} {KNOWN.get(word,'?')}")
    except Exception as e:
        print(f"{path:20s} ERROR: {e}")

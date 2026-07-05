#!/usr/bin/env python3
"""Bake cheats into hack.nds. By default produces one ROM:
  hack_dp4x.nds     - DP x4 only (single in-place instruction patch; safe/verified)
The DP x4 + Save Anywhere variant (hack_dp4x_save.nds) is disabled at the bottom of
this file because the RAM-scratch payload site is not runtime-verifiable here
(experimental); uncomment to build it.
All patched values are exactly what the original Action Replay codes write.
"""
import struct
import ndspy.rom
import ndspy.code
from capstone import Cs, CS_ARCH_ARM, CS_MODE_ARM
MD = Cs(CS_ARCH_ARM, CS_MODE_ARM)

# --- DP multiplier (ov3) ---
DP_OV, DP_OFF, DP_VAL = 3, 0x40EB4, 0x10800107          # addne r0,r0,r7,lsl#2  (4x)

# --- Save Anywhere ---
SA_OV, SA_HOOK_OFF, SA_HOOK_VAL = 31, 0xF6A8, 0x0AFA4FCC  # ov31 0x0216C1C8: beq 0x02000100
SA_ARM9_OFF = 0x100                                        # ARM9 0x02000100
SA_PAYLOAD = [0xE3100004,0x0A05B03F,0xE92D000F,0xE3A00B02,0xE59F1020,0xE5911000,
              0xE2811004,0xE3A02C1A,0xE2822020,0xE3A03801,0xE2433001,0xEB059589,
              0xE8BD000F,0xEA05B033,0x02198408]            # 14 instrs + pointer @0x138


def bake(do_save_anywhere, out):
    rom = ndspy.rom.NintendoDSRom.fromFile('roms/hack.nds')
    ovs = rom.loadArm9Overlays()

    # DP patch
    ov3 = ovs[DP_OV]
    d3 = bytearray(ov3.data)
    assert struct.unpack_from('<I', d3, DP_OFF-4)[0] == 0x05897060
    assert struct.unpack_from('<I', d3, DP_OFF)[0] == 0x10800007
    struct.pack_into('<I', d3, DP_OFF, DP_VAL)
    ov3.data = bytes(d3)
    rom.files[ov3.fileID] = ov3.save(compress=True)

    if do_save_anywhere:
        # hook patch in ov31
        ov31 = ovs[SA_OV]
        d31 = bytearray(ov31.data)
        assert struct.unpack_from('<I', d31, SA_HOOK_OFF)[0] == 0x0A00000E
        struct.pack_into('<I', d31, SA_HOOK_OFF, SA_HOOK_VAL)
        ov31.data = bytes(d31)
        rom.files[ov31.fileID] = ov31.save(compress=True)
        # payload in ARM9 0x02000100
        a9 = rom.loadArm9()
        sec = a9.sections[0]
        ds = bytearray(sec.data)
        for i, w in enumerate(SA_PAYLOAD):
            struct.pack_into('<I', ds, SA_ARM9_OFF + i*4, w)
        sec.data = bytes(ds)
        rom.arm9 = a9.save(compress=True)

    rom.arm9OverlayTable = ndspy.code.saveOverlayTable(ovs)
    rom.saveToFile(out)
    return rom


def verify(out, expect_save):
    r = ndspy.rom.NintendoDSRom.fromFile(out)
    ov3 = r.loadArm9Overlays()[DP_OV]
    dp = struct.unpack_from('<I', ov3.data, DP_OFF)[0]
    print(f"[{out}] DP @0x02182694 = 0x{dp:08X}  {'OK' if dp==DP_VAL else 'FAIL'}")
    if expect_save:
        ov31 = r.loadArm9Overlays()[SA_OV]
        hook = struct.unpack_from('<I', ov31.data, SA_HOOK_OFF)[0]
        sec = r.loadArm9().sections[0]
        pay = [struct.unpack_from('<I', sec.data, SA_ARM9_OFF+i*4)[0] for i in range(len(SA_PAYLOAD))]
        ok = hook==SA_HOOK_VAL and pay==SA_PAYLOAD
        print(f"[{out}] hook @0x0216C1C8 = 0x{hook:08X}  payload@0x02000100 match={pay==SA_PAYLOAD}  {'OK' if ok else 'FAIL'}")
        # disasm proof
        blob = b''.join(struct.pack('<I', w) for w in SA_PAYLOAD[:14])
        print("  baked payload disassembly:")
        for ins in MD.disasm(blob, 0x02000100):
            print(f"    0x{ins.address:08X}: {ins.mnemonic} {ins.op_str}")
        for ins in MD.disasm(struct.pack('<I', hook), 0x0216C1C8):
            print(f"    hook 0x0216C1C8: {ins.mnemonic} {ins.op_str}")
    # integrity
    ok=True
    try:
        r.loadArm9()
        for i in sorted(r.loadArm9Overlays()): _=r.loadArm9Overlays()[i].data
    except Exception as e: ok=False; print("  integrity ERROR:", e)
    print(f"[{out}] integrity: {'OK' if ok else 'BROKEN'}")


bake(False, 'roms/hack_dp4x.nds');      verify('roms/hack_dp4x.nds', False)
# print()
# bake(True, 'roms/hack_dp4x_save.nds');  verify('roms/hack_dp4x_save.nds', True)

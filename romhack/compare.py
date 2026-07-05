#!/usr/bin/env python3
"""Definitive base-vs-hack comparison at the ndspy level (decompressed)."""
import ndspy.rom

b = ndspy.rom.NintendoDSRom.fromFile('roms/base.nds')
h = ndspy.rom.NintendoDSRom.fromFile('roms/hack.nds')

# ARM9 sections
ba = b.loadArm9(); ha = h.loadArm9()
print("== ARM9 sections (decompressed) ==")
print(f"  base sections: {len(ba.sections)}  hack sections: {len(ha.sections)}")
for i,(s,t) in enumerate(zip(ba.sections, ha.sections)):
    same = bytes(s.data) == bytes(t.data)
    # count differing bytes if same length
    n = min(len(s.data), len(t.data))
    diffs = sum(1 for k in range(n) if s.data[k] != t.data[k]) if not same else 0
    print(f"  sec{i}: ram=0x{s.ramAddress:08X} blen=0x{len(s.data):X} hlen=0x{len(t.data):X} "
          f"identical={same} differing_bytes={diffs}")

# Overlays
bo = b.loadArm9Overlays(); ho = h.loadArm9Overlays()
print("== Overlays (decompressed) ==")
diff_ovs = []
for i in sorted(bo):
    sd = bytes(bo[i].data); td = bytes(ho[i].data)
    if sd != td:
        n = min(len(sd), len(td))
        diffs = sum(1 for k in range(n) if sd[k] != td[k])
        diff_ovs.append(i)
        print(f"  ov{i:02d}: DIFFERS  blen=0x{len(sd):X} hlen=0x{len(td):X} differing_bytes={diffs}")
print(f"  overlays differing: {diff_ovs if diff_ovs else 'NONE'}")

# Explicit check on the two hook overlays
for i in (3, 31):
    same = bytes(bo[i].data) == bytes(ho[i].data)
    print(f"  >>> ov{i:02d} base==hack ? {same} "
          f"(ram=0x{bo[i].ramAddress:08X}==0x{ho[i].ramAddress:08X}:{bo[i].ramAddress==ho[i].ramAddress})")

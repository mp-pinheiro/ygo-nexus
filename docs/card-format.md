# Over the Nexus / Nexus Revival — card data format

Reverse-engineered from the ROM and validated against
[ProjectIgnis/BabelCDB](https://github.com/ProjectIgnis/BabelCDB) `cards.cdb` by joining
on card password (4071 cards matched: ATK/DEF/Level/Attribute/Race all decode at ≥99.8%).

All card data lives in `data/Data_arc_pac/bin2.pac`. Between base and the hack, only
`card_pack.bin` differs — names/text/stats are identical.

## PAC container (`bin2.pac`)

Konami slot-table archive (see `cardtool/pac.py`, ported from
[YgoNdsRandomizer](https://github.com/mSpoeth/YgoNdsRandomizer)):

```
[0 .. nameEnd)   ASCII filename table; entries are [lenByte][flagByte][name],
                 lenByte in 0x0A..0x18 doubling as the separator.
                 nameEnd = offset of first 0xFFFF marker, rounded down to 16.
[nameEnd ..]     0xFFFF pad + 8-byte-per-file record table: u32 addr (LE), u32 size (LE).
                 First record and size==0 records skipped; table ends at first
                 all-zero 16-byte line. addr is relative to the data section.
```

99 sub-files. Relevant English ones (suffix `_e`; also `_f _g _i _s _j _k _r` per language):

| file | per-card | contents |
|------|----------|----------|
| `card_indx_e.bin` | 8 B | `[u32 name_off][u32 desc_off]` into name/desc blobs; N+1 records (last = sentinel) |
| `card_name_e.bin` | var | NUL-terminated card names (Latin-1/ANSI) |
| `card_desc_e.bin` | var | NUL-terminated effect/flavor text |
| `card_prop.bin`   | 8 B | bit-packed stats (below) |
| `card_pass.bin`   | 4 B | u32 card password (0 = none) |
| `card_pack.bin`   | 8 B | `[0]=rarity [1]=bonusRarity [3]=pack [4]=bonusPack` (**hack rewrites this**) |
| `card_genre.bin`  | 8 B | archetype/genre bitfield (not yet decoded) |

Card at sequential index `i`: name = `card_name_e[name_off[i]]`, desc = `card_desc_e[desc_off[i]]`.

## `card_prop.bin` — two little-endian uint32 per card

```
Prop1 (bytes 0-3):  id   = bits  0..13   (14b, internal id)
                    atk  = bits 14..22   (9b)  * 10   ; 511 -> "?" (variable)
                    def  = bits 23..31   (9b)  * 10   ; 511 -> "?"

Prop2 (bytes 4-7):  kind = bits  0..5    (6b)  enum, see below
                    attr = bits  6..9    (4b)  1 LIGHT 2 DARK 3 WATER 4 FIRE 5 EARTH 6 WIND 7 DIVINE
                    lvl  = bits 10..13   (4b)
                    icon = bits 14..16   (3b)  spell/trap: 1 Counter 2 Field 3 Equip 4 Continuous 5 Quick-Play 6 Ritual
                    race = bits 17..21   (5b)  monster type, see below
```

**kind** (`Prop2 & 0x3F`): 1 Normal · 3 Effect · 5 Fusion · 7 Fusion/Effect · 9 Ritual ·
11 Ritual/Effect · 13 Toon · 15 Spirit · 17 Union · 19 Gemini · 27 Spell · 29 Trap ·
31 Normal Tuner · 33 Effect Tuner · 35 Synchro · 37 Synchro/Effect · 39 Synchro/Effect/Tuner.

**race** (`(Prop2>>17) & 0x1F`): 1 Dragon · 2 Zombie · 3 Fiend · 4 Pyro · 5 Sea Serpent ·
6 Rock · 7 Machine · 8 Fish · 9 Dinosaur · 10 Insect · 11 Beast · 12 Beast-Warrior ·
13 Plant · 14 Aqua · 15 Warrior · 16 Winged Beast · 17 Fairy · 18 Spellcaster · 19 Thunder ·
20 Reptile · 21 Psychic · 22 Divine-Beast.

Enum layout confirmed against the Tag Force editor
[xan1242/TFCardEditGUI](https://github.com/xan1242/TFCardEditGUI) (`TFCard.cs`), whose field
*widths* match; WC2011 shifts several Prop2 fields by +2 bits vs Tag Force and widens the id.

Trap Monsters (Embodiment of Apophis, Zoma the Spirit, ...) are stored in trap form
(atk/def 0); the cdb lists their monster stats, so those 5 rows "mismatch" by design.

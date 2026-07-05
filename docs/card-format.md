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

Pack **names** live in `bin.pac` → `pack_nameeng.bin`, indexed by `pack_indxeng.bin` (8-byte
records `[name_off][desc_off]` per pack; record 0 = none). `card_pack.bin`'s `pack` id selects
the record — e.g. in the hack, id 28 → `TDGS`. Base uses full set names ("THE DUELIST GENESIS").

**Card art** is in `card.pac` as 8612 uncompressed NTBG images = 4306 24×32 followed by 4306
64×64, both in card-index order — so card `i`'s 64×64 art is the `(4306 + i)`-th NTBG. Unlike
external art (keyed by password), this is distinct per entry, so it resolves alt-arts and the
password-0 God cards. Pack/card art share the NTBG format below.

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

**kind** (`Prop2 & 0x3F`) decodes to a set of composing type tags — a Toon/Fusion/Synchro/…
monster is *also* an Effect monster: 1 Normal · 3 Effect · 5 Fusion · 7 Fusion+Effect ·
9 Ritual · 11 Ritual+Effect · 13 Toon+Effect · 15 Spirit+Effect · 17 Union+Effect ·
19 Gemini+Effect · 21 Token · 27 Spell · 29 Trap · 31 Normal+Tuner · 33 Effect+Tuner ·
35 Synchro · 37 Synchro+Effect · 39 Synchro+Effect+Tuner.

**race** (`(Prop2>>17) & 0x1F`): 1 Dragon · 2 Zombie · 3 Fiend · 4 Pyro · 5 Sea Serpent ·
6 Rock · 7 Machine · 8 Fish · 9 Dinosaur · 10 Insect · 11 Beast · 12 Beast-Warrior ·
13 Plant · 14 Aqua · 15 Warrior · 16 Winged Beast · 17 Fairy · 18 Spellcaster · 19 Thunder ·
20 Reptile · 21 Psychic · 22 Divine-Beast.

Enum layout confirmed against the Tag Force editor
[xan1242/TFCardEditGUI](https://github.com/xan1242/TFCardEditGUI) (`TFCard.cs`), whose field
*widths* match; WC2011 shifts several Prop2 fields by +2 bits vs Tag Force and widens the id.

Trap Monsters (Embodiment of Apophis, Zoma the Spirit, ...) are stored in trap form
(atk/def 0); the cdb lists their monster stats, so those 5 rows "mismatch" by design.

## Forbidden/Limited lists (`bin.pac` → `limit*.bin`)

The deck editor's banlist. `bin.pac` carries six historical revisions —
`limit200609`, `limit200703`, `limit200709`, `limit200809`, `limit200909`, `limit201009` —
one per OCG Forbidden/Limited List. `limit201009.bin` (OCG September 2010) is the newest and
the shipped default (47 Forbidden / 67 Limited / 18 Semi-Limited); the rest are the older
selectable lists.

```
u16         total       number of restricted entries
u16         revision    list id (increments per revision); unused by the decoder
u32         0           padding
u16[total]  entries     tier = v >> 14    (0 Forbidden, 1 Limited, 2 Semi-Limited)
                        id   = v & 0x3FFF (14b internal id, same as card_prop)
```

Only restricted cards are listed; any id absent from the table is Unlimited (3 copies).
Keyed by the 14-bit internal id, **not** the sequential card index.

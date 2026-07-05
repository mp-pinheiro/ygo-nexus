# ygo-nexus-cht

Tooling for **Yu-Gi-Oh! 5D's World Championship 2011: Over the Nexus** (`BYYE`) and the
**Nexus Revival** romhack. Two independent toolchains:

- **`cardtool/`** — extracts the full card database from the ROM and serves a fast,
  text-searchable card browser (the in-game deck editor has no text search).
- **`romhack/`** — the ARM9/overlay reverse-engineering + cheat-baking scripts
  (DP multiplier, Save-Anywhere, save analysis).

## Layout

```
cardtool/     pac.py (PAC archive unpacker), extract.py (-> data/cards.json + web bundle)
  web/        index.html + cards.js — open in a browser to search
romhack/      analyze, disasm, compare, bake_dp, bake_all, check_dp, re_* (run from repo root)
data/         cards.json (generated), cards.cdb (ground-truth, git-ignored)
roms/         base.nds, hack.nds, hack_dp*.nds            (git-ignored)
saves/        base.sav                                     (git-ignored)
cheats/       base.cht (Action Replay), base.mch (melonDS)
extracted/    base_x/, hack_x/ — `ndstool -x` output       (git-ignored, derived)
vendor/       ndstool/, melonDS.exe                         (git-ignored)
docs/         card-format.md — reverse-engineered binary format spec
```

Copyrighted ROMs, saves, the emulator, extracted filesystems, and the generated/external
card databases are git-ignored — everything under them is reproducible from the ROM.

## Setup

```sh
uv sync            # installs ndspy + capstone into .venv
```

## Card search tool

The card database lives in `bin2.pac` inside the ROM. Build it, then open the browser:

```sh
.venv/bin/python cardtool/extract.py      # -> data/cards.json + cardtool/web/cards.js
```

Then open `cardtool/web/index.html` in a browser. Search by name/effect text and filter
by ATK/DEF/level/attribute/type/race/kind.

`extract.py` cross-validates its ROM decode against `data/cards.cdb`
([ProjectIgnis/BabelCDB](https://github.com/ProjectIgnis/BabelCDB), joined by card
password). The cdb is optional — extraction works without it; validation is skipped.

**Note:** Nexus Revival only rewrites `card_pack.bin` (pack contents); card names, text,
and stats are identical to base Over the Nexus.

## Romhack scripts

Read-only analysis + in-place cheat baking, all run **from the repo root**:

```sh
.venv/bin/python romhack/check_dp.py                 # report DP multiplier in every roms/*.nds
.venv/bin/python romhack/bake_dp.py 4                # -> roms/hack_dp4x.nds
```

See `docs/card-format.md` for the reverse-engineered binary formats.

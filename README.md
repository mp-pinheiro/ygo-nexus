# ygo-nexus-cht

Tooling for **Yu-Gi-Oh! 5D's World Championship 2011: Over the Nexus** (`BYYE`) and the
**Nexus Revival** romhack. Two independent toolchains:

- **`cardtool/`** — extracts the full card database from the ROM and serves a fast,
  text-searchable card browser (the in-game deck editor has no text search).
- **`romhack/`** — the ARM9/overlay reverse-engineering + cheat-baking scripts
  (DP multiplier, Save-Anywhere, save analysis).

## Layout

```
cardtool/     pac.py (PAC archive unpacker), extract.py (-> data/cards.json + web public/)
  web/        Vite + Svelte 5 app (src/, public/, index.html, vite.config.js) — served, not file://
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

The card database lives in `bin2.pac` inside the ROM. `extract.py` writes the database and
art straight into `cardtool/web/public/` (`cards.json`, `cardart/`, `packs/`), which the
browser app serves:

```sh
.venv/bin/python cardtool/extract.py      # -> data/cards.json + cardtool/web/public/
just web-install                          # install web deps (run once)
just web-dev                              # Vite dev server -> http://localhost:5173
```

Then open `http://localhost:5173`. Search by name/effect text and filter by
ATK/DEF/level/attribute/type/race/kind.

To build a production bundle run `just web-build` (output in `cardtool/web/dist/`), then
`just web-preview` to preview it at `http://localhost:4173` — or serve the build without
Node via `python -m http.server -d cardtool/web/dist`.

The browser is now a served Vite + Svelte 5 app — the old `file://` "open index.html
directly" workflow is gone, and the web workflow needs Node 20.19+ / 22.12+ (the Python
extract step is unchanged).

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

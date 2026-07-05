#!/usr/bin/env python3
"""Extract the full card database from Over the Nexus / Nexus Revival into cards.json.

Card text + stats live in bin2.pac (identical between base and the hack); the hack
only rewrites card_pack.bin. We read everything from the hack's bin2.pac so pack
membership reflects Nexus Revival. card_prop.bin layout (two LE uint32 per card),
reverse-engineered and validated against ProjectIgnis/BabelCDB by password:

  Prop1: id=[0:14]  atk=[14:23]*10  def=[23:32]*10     (atk/def 511 -> "?")
  Prop2: kind=[0:6] attr=[6:10] level=[10:14] icon=[14:17] race=[17:22]
"""
import json
import struct
from pathlib import Path

import pac

REPO = Path(__file__).resolve().parents[1]
BIN2 = REPO / 'extracted/hack_x/data/Data_arc_pac/bin2.pac'   # hack card data (== base) + hack packs
CDB = REPO / 'data/cards.cdb'                                 # ground-truth (ProjectIgnis/BabelCDB)
CARDS_JSON = REPO / 'data/cards.json'
CARDS_JS = REPO / 'cardtool/web/cards.js'

ATTR = {1: 'LIGHT', 2: 'DARK', 3: 'WATER', 4: 'FIRE', 5: 'EARTH', 6: 'WIND', 7: 'DIVINE'}
RACE = {1: 'Dragon', 2: 'Zombie', 3: 'Fiend', 4: 'Pyro', 5: 'Sea Serpent', 6: 'Rock',
        7: 'Machine', 8: 'Fish', 9: 'Dinosaur', 10: 'Insect', 11: 'Beast', 12: 'Beast-Warrior',
        13: 'Plant', 14: 'Aqua', 15: 'Warrior', 16: 'Winged Beast', 17: 'Fairy', 18: 'Spellcaster',
        19: 'Thunder', 20: 'Reptile', 21: 'Psychic', 22: 'Divine-Beast'}
ICON = {0: None, 1: 'Counter', 2: 'Field', 3: 'Equip', 4: 'Continuous', 5: 'Quick-Play', 6: 'Ritual'}
# Prop2 & 0x3F -> (cardType, kind label, is_tuner)
KIND = {
    1:  ('Monster', 'Normal', False),   3:  ('Monster', 'Effect', False),
    5:  ('Monster', 'Fusion', False),   7:  ('Monster', 'Fusion/Effect', False),
    9:  ('Monster', 'Ritual', False),   11: ('Monster', 'Ritual/Effect', False),
    13: ('Monster', 'Toon', False),     15: ('Monster', 'Spirit', False),
    17: ('Monster', 'Union', False),    19: ('Monster', 'Gemini', False),
    27: ('Spell', 'Spell', False),      29: ('Trap', 'Trap', False),
    31: ('Monster', 'Normal', True),    33: ('Monster', 'Effect', True),
    35: ('Monster', 'Synchro', False),  37: ('Monster', 'Synchro/Effect', False),
    39: ('Monster', 'Synchro/Effect', True),
}


def cstr(buf, off):
    end = buf.find(b'\x00', off)
    return buf[off:end].decode('latin1')


def extract(bin2_path=BIN2):
    files = pac.unpack(open(bin2_path, 'rb').read())
    indx, name, desc = files['card_indx_e.bin'], files['card_name_e.bin'], files['card_desc_e.bin']
    prop, passwd, pack = files['card_prop.bin'], files['card_pass.bin'], files['card_pack.bin']
    n = len(indx) // 8 - 1                       # last record is the offset sentinel

    cards = []
    for i in range(n):
        noff, doff = struct.unpack_from('<II', indx, i * 8)
        nm = cstr(name, noff)
        if not nm:
            continue                             # empty slot
        p1, p2 = struct.unpack_from('<II', prop, i * 8)
        kraw = p2 & 0x3F
        ctype, kind, tuner = KIND.get(kraw, ('Monster', f'?0x{kraw:02X}', False))
        atk_r, def_r = (p1 >> 14) & 0x1FF, (p1 >> 23) & 0x1FF
        pw = struct.unpack_from('<I', passwd, i * 4)[0]
        rarity, pack_id = pack[i * 8], pack[i * 8 + 3]

        card = {
            'idx': i,
            'id': p1 & 0x3FFF,
            'name': nm,
            'effect': cstr(desc, doff),
            'password': pw or None,
            'cardType': ctype,
            'kind': kind,
            'tuner': tuner,
            'attribute': ATTR.get((p2 >> 6) & 0xF) if ctype == 'Monster' else None,
            'race': RACE.get((p2 >> 17) & 0x1F) if ctype == 'Monster' else None,
            'level': (p2 >> 10) & 0xF if ctype == 'Monster' else None,
            'atk': '?' if atk_r == 0x1FF else atk_r * 10,
            'def': '?' if def_r == 0x1FF else def_r * 10,
            'icon': ICON.get((p2 >> 14) & 0x7) if ctype != 'Monster' else None,
            'pack': pack_id or None,
            'rarity': rarity or None,
        }
        cards.append(card)
    return cards


def validate(cards):
    """Cross-check ROM decode against cards.cdb by password; report mismatches."""
    try:
        import sqlite3
    except ImportError:
        return
    if not CDB.exists():
        print("  (skipping validation: data/cards.cdb not present)")
        return
    con = sqlite3.connect(CDB)
    ya = {16: 'LIGHT', 32: 'DARK', 2: 'WATER', 4: 'FIRE', 1: 'EARTH', 8: 'WIND', 64: 'DIVINE'}
    cdb = {pid: (atk, dfn, lvl, attr) for pid, atk, dfn, lvl, attr in
           con.execute('select id,atk,def,level,attribute from datas')}
    m = bad_atk = bad_attr = 0
    for c in cards:
        if not c['password'] or c['password'] not in cdb:
            continue
        catk, cdef, clvl, cattr = cdb[c['password']]
        m += 1
        if catk >= 0 and c['atk'] != '?' and c['atk'] != catk:
            bad_atk += 1
        if cattr in ya and c['attribute'] and c['attribute'] != ya[cattr]:
            bad_attr += 1
    print(f"  validated {m} cards vs cards.cdb: atk mismatches={bad_atk} attr mismatches={bad_attr}")


if __name__ == '__main__':
    cards = extract()
    db = {'game': 'Yu-Gi-Oh! WC2011 Over the Nexus / Nexus Revival', 'count': len(cards),
          'cards': cards}
    blob = json.dumps(db, ensure_ascii=False, separators=(',', ':'))
    CARDS_JSON.write_text(blob)
    # cards.js lets index.html run offline over file:// (no fetch/CORS needed)
    CARDS_JS.write_text('window.CARD_DB = ' + blob + ';')
    mon = sum(1 for c in cards if c['cardType'] == 'Monster')
    sp = sum(1 for c in cards if c['cardType'] == 'Spell')
    tr = sum(1 for c in cards if c['cardType'] == 'Trap')
    print(f"wrote {CARDS_JSON} + {CARDS_JS}: {len(cards)} cards ({mon} monster / {sp} spell / {tr} trap)")
    validate(cards)

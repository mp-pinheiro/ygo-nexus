#!/usr/bin/env python3
"""Extract the full card database from Over the Nexus / Nexus Revival into cards.json.

Card text + stats live in bin2.pac (identical between base and the hack); the hack
only rewrites card_pack.bin. We read everything from the hack's bin2.pac so pack
membership reflects Nexus Revival. card_prop.bin layout (two LE uint32 per card),
reverse-engineered and validated against ProjectIgnis/BabelCDB by password:

  Prop1: id=[0:14]  atk=[14:23]*10  def=[23:32]*10     (511 = variable "?", stored as 0)
  Prop2: kind=[0:6] attr=[6:10] level=[10:14] icon=[14:17] race=[17:22]
"""
import json
import sqlite3
import struct
from pathlib import Path

import pac
import packimg

REPO = Path(__file__).resolve().parents[1]
BIN2 = REPO / 'extracted/hack_x/data/Data_arc_pac/bin2.pac'   # hack card data (== base) + hack packs
BIN1 = REPO / 'extracted/hack_x/data/Data_arc_pac/bin.pac'    # pack names + index
PACKPAC = REPO / 'extracted/hack_x/data/Data_arc_pac/pack.pac'  # pack box art
CARDPAC = REPO / 'extracted/hack_x/data/Data_arc_pac/card.pac'  # per-card 64x64 art
CDB = REPO / 'data/cards.cdb'                                 # ground-truth (ProjectIgnis/BabelCDB)
CARDS_JSON = REPO / 'data/cards.json'
CARDS_JS = REPO / 'cardtool/web/cards.js'
PACKS_DIR = REPO / 'cardtool/web/packs'
CARDART_DIR = REPO / 'cardtool/web/cardart'
RARITY = {0: 'Common', 4: 'Rare', 3: 'Super Rare', 2: 'Ultra Rare'}

ATTR = {1: 'LIGHT', 2: 'DARK', 3: 'WATER', 4: 'FIRE', 5: 'EARTH', 6: 'WIND', 7: 'DIVINE'}
RACE = {1: 'Dragon', 2: 'Zombie', 3: 'Fiend', 4: 'Pyro', 5: 'Sea Serpent', 6: 'Rock',
        7: 'Machine', 8: 'Fish', 9: 'Dinosaur', 10: 'Insect', 11: 'Beast', 12: 'Beast-Warrior',
        13: 'Plant', 14: 'Aqua', 15: 'Warrior', 16: 'Winged Beast', 17: 'Fairy', 18: 'Spellcaster',
        19: 'Thunder', 20: 'Reptile', 21: 'Psychic', 22: 'Divine-Beast'}
ICON = {0: None, 1: 'Counter', 2: 'Field', 3: 'Equip', 4: 'Continuous', 5: 'Quick-Play', 6: 'Ritual'}
# Prop2 & 0x3F -> (cardType, type tags). Tags compose: a Toon or Fusion monster is
# also an Effect monster, so filtering by "Effect" must catch all of them.
KIND = {
    1:  ('Monster', ['Normal']),          3:  ('Monster', ['Effect']),
    5:  ('Monster', ['Fusion']),          7:  ('Monster', ['Fusion', 'Effect']),
    9:  ('Monster', ['Ritual']),          11: ('Monster', ['Ritual', 'Effect']),
    13: ('Monster', ['Toon', 'Effect']),  15: ('Monster', ['Spirit', 'Effect']),
    17: ('Monster', ['Union', 'Effect']), 19: ('Monster', ['Gemini', 'Effect']),
    21: ('Monster', ['Token']),
    27: ('Spell', ['Spell']),             29: ('Trap', ['Trap']),
    31: ('Monster', ['Normal', 'Tuner']), 33: ('Monster', ['Effect', 'Tuner']),
    35: ('Monster', ['Synchro']),         37: ('Monster', ['Synchro', 'Effect']),
    39: ('Monster', ['Synchro', 'Effect', 'Tuner']),
}
TAG_ORDER = ['Fusion', 'Ritual', 'Synchro', 'Toon', 'Spirit', 'Union', 'Gemini',
             'Normal', 'Tuner', 'Effect', 'Token', 'Spell', 'Trap']


def cstr(buf, off):
    end = buf.find(b'\x00', off)
    return buf[off:end].decode('latin1')


def build_packs():
    b1 = pac.unpack(open(BIN1, 'rb').read())
    names, desc, indx = b1['pack_nameeng.bin'], b1['pack_desceng.bin'], b1['pack_indxeng.bin']
    pp = pac.unpack(open(PACKPAC, 'rb').read())
    PACKS_DIR.mkdir(parents=True, exist_ok=True)
    out = {}
    for pid in range(1, len(indx) // 8):
        noff, doff = struct.unpack_from('<II', indx, pid * 8)
        code = names[noff:names.find(b'\x00', noff)].decode('cp1252', 'replace').strip()
        if not code:
            continue
        full = desc[doff:desc.find(b'\x00', doff)].decode('cp1252', 'replace').strip()
        img = None
        key = f'l_pack{pid:02d}.lz5bg'
        if key in pp:
            pic = packimg.decode(pp[key])
            if pic:
                pic.save(PACKS_DIR / f'{pid}.png')
                img = f'packs/{pid}.png'
        out[pid] = {'code': code, 'full': full, 'img': img}
    return out


def image_ids():
    """cdb name->id (main artwork) and the set of ids, to resolve ygoprodeck art for
    cards whose ROM password is 0 (e.g. the Egyptian Gods -> 10000000, ...)."""
    if not CDB.exists():
        return {}, set()
    con = sqlite3.connect(CDB)
    idset = {i for (i,) in con.execute('select id from datas')}
    name2id = {}
    for name, i in con.execute('select t.name, d.id from datas d join texts t on d.id=t.id order by d.alias'):
        name2id.setdefault(name.lower(), i)
    return name2id, idset


def card_art_offsets():
    """Return (card.pac bytes, NTBG image offsets); see docs/card-format.md."""
    raw = open(CARDPAC, 'rb').read()
    offs, i = [], 0
    while True:
        j = raw.find(b'NTBG', i)
        if j < 0:
            break
        offs.append(j); i = j + 4
    return raw, offs


def extract(bin2_path=BIN2):
    files = pac.unpack(open(bin2_path, 'rb').read())
    indx, name, desc = files['card_indx_e.bin'], files['card_name_e.bin'], files['card_desc_e.bin']
    prop, passwd, pack = files['card_prop.bin'], files['card_pass.bin'], files['card_pack.bin']
    packs = build_packs()
    name2id, idset = image_ids()
    art_raw, art_offs = card_art_offsets()
    art_base = len(art_offs) // 2
    CARDART_DIR.mkdir(parents=True, exist_ok=True)
    n = len(indx) // 8 - 1                       # last record is the offset sentinel

    cards = []
    for i in range(n):
        noff, doff = struct.unpack_from('<II', indx, i * 8)
        nm = cstr(name, noff)
        if not nm:
            continue                             # empty slot
        p1, p2 = struct.unpack_from('<II', prop, i * 8)
        kraw = p2 & 0x3F
        ctype, tags = KIND.get(kraw, ('Monster', [f'?0x{kraw:02X}']))
        tags = sorted(tags, key=lambda t: TAG_ORDER.index(t) if t in TAG_ORDER else 99)
        atk_r, def_r = (p1 >> 14) & 0x1FF, (p1 >> 23) & 0x1FF
        pw = struct.unpack_from('<I', passwd, i * 4)[0]
        rarity, pack_id = pack[i * 8], pack[i * 8 + 3]
        aj = art_offs[art_base + i]
        packimg.decode_ntbg(art_raw[aj:aj + struct.unpack_from('<I', art_raw, aj + 8)[0]]).save(CARDART_DIR / f'{i}.png')

        card = {
            'idx': i,
            'id': p1 & 0x3FFF,
            'name': nm,
            'effect': cstr(desc, doff),
            'password': pw or None,
            'imgId': pw if (pw and pw in idset) else name2id.get(nm.lower()),
            'art': f'cardart/{i}.png',
            'cardType': ctype,
            'types': tags,
            'kind': '/'.join(tags),
            'attribute': ATTR.get((p2 >> 6) & 0xF) if ctype == 'Monster' else None,
            'race': RACE.get((p2 >> 17) & 0x1F) if ctype == 'Monster' else None,
            'level': (p2 >> 10) & 0xF if ctype == 'Monster' else None,
            'atk': (0 if atk_r == 0x1FF else atk_r * 10) if ctype == 'Monster' else None,
            'def': (0 if def_r == 0x1FF else def_r * 10) if ctype == 'Monster' else None,
            'icon': ICON.get((p2 >> 14) & 0x7) if ctype != 'Monster' else None,
            'pack': packs[pack_id]['code'] if pack_id in packs else None,
            'rarity': RARITY.get(rarity) if pack_id else None,
        }
        cards.append(card)
    return cards, packs


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
        if c['cardType'] == 'Monster' and catk >= 0 and c['atk'] not in (None, '?') and c['atk'] != catk:
            bad_atk += 1
        if cattr in ya and c['attribute'] and c['attribute'] != ya[cattr]:
            bad_attr += 1
    print(f"  validated {m} cards vs cards.cdb: atk mismatches={bad_atk} attr mismatches={bad_attr}")


if __name__ == '__main__':
    cards, packs = extract()
    packs_by_code = {m['code']: {'full': m['full'], 'img': m['img']} for m in packs.values()}
    db = {'game': 'Yu-Gi-Oh! WC2011 Over the Nexus / Nexus Revival', 'count': len(cards),
          'packs': packs_by_code, 'cards': cards}
    blob = json.dumps(db, ensure_ascii=False, separators=(',', ':'))
    CARDS_JSON.write_text(blob)
    # cards.js lets index.html run offline over file:// (no fetch/CORS needed)
    CARDS_JS.write_text('window.CARD_DB = ' + blob + ';')
    mon = sum(1 for c in cards if c['cardType'] == 'Monster')
    sp = sum(1 for c in cards if c['cardType'] == 'Spell')
    tr = sum(1 for c in cards if c['cardType'] == 'Trap')
    print(f"wrote {CARDS_JSON} + {CARDS_JS}: {len(cards)} cards ({mon} monster / {sp} spell / {tr} trap)")
    validate(cards)

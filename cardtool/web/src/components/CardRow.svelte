<script>
  import { rowAction } from '../lib/stores/ui.svelte.js'
  import { add, sectionOf } from '../lib/stores/deck.svelte.js'
  import { showToast } from '../lib/stores/toast.svelte.js'
  import { media } from '../lib/stores/media.svelte.js'
  import { owned } from '../lib/stores/owned.svelte.js'
  import LimitBadge from './LimitBadge.svelte'

  let { card } = $props()

  const base = import.meta.env.VITE_DATA_BASE || import.meta.env.BASE_URL

  // Name/thumbnail -> details (rowAction); else add to Main/Extra (Shift-click
  // adds to Side). Touch gets a confirmation toast on success because it has
  // no hover/title affordance to signal what the tap did.
  function rowClick(e) {
    rowAction(e, card, () => {
      const section = e.shiftKey ? 'side' : sectionOf(card)
      const r = add(card, section)
      if (!r.ok) showToast(r.reason)
      else if (media.coarse) {
        showToast(`Added to ${section === 'extra' ? 'Extra' : section === 'side' ? 'Side' : 'Main'}: ${card.name}`)
      }
    })
  }

  // Compact meta for the mobile sub-line (mirrors CardDetail's meta line; the
  // type itself is shown as a badge, so non-monsters only add the icon).
  const msLine = $derived(
    card.cardType === 'Monster'
      ? [card.attribute, card.race, card.kind].filter(Boolean).join(' · ')
      : card.icon || '',
  )
</script>

<tr data-i={card.idx} onclick={rowClick} title="Click to add · Shift-click for Side">
  <td class="thumb" data-details>
    <img class="pix" src={base + card.art} loading="lazy" alt="" />
    {#if owned.loaded}<span class="own-ct">{owned.copies(card.idx)}</span>{/if}
  </td>
  <td class="name">
    <span class="nm" data-details>{card.name}</span>
    <div class="msub">
      <span class="badge t-{card.cardType}">{card.cardType}</span>
      {#if msLine}<span>{msLine}</span>{/if}
      {#if card.cardType === 'Monster'}
        <span class="mlvl">
          {#if card.level != null}<span class="mstars" title="Level {card.level}">{'★'.repeat(Math.min(card.level, 12))}</span>{/if}
          {card.atk ?? '—'} / {card.def ?? '—'}
        </span>
      {/if}
    </div>
    {#if card.effect}<div class="meff">{card.effect}</div>{/if}
  </td>
  <td class="lim">{#if card.limit}<LimitBadge limit={card.limit} />{/if}</td>
  <td class="c-type"><span class="badge t-{card.cardType}">{card.cardType}</span></td>
  <td class="c-attr">{#if card.attribute}<span class="sub">{card.attribute}</span>{/if}</td>
  <td class="sub c-race">{card.race || ''}</td>
  <td class="sub c-kind">{card.kind}</td>
  <td class="num c-lv">{card.level ?? ''}</td>
  <td class="num c-atk">{card.atk ?? ''}</td>
  <td class="num c-def">{card.def ?? ''}</td>
  <td class="c-eff"><div class="eff">{card.effect || ''}</div></td>
</tr>

<style>
  tr { border-bottom:1px solid var(--line); cursor:pointer; user-select:none; }
  tr:hover { background:var(--panel2); }
  td { padding:7px 10px; vertical-align:top; }
  td.name { font-weight:600; }
  td.num { text-align:right; font-variant-numeric:tabular-nums; color:var(--dim); }
  td.lim { width:1px; text-align:center; }
  td.thumb { padding:4px 4px 4px 12px; width:1px; position:relative; }
  td.thumb img { width:34px; height:34px; object-fit:cover; image-rendering:pixelated;
    border-radius:4px; background:var(--panel2); display:block; }
  .own-ct { position:absolute; bottom:2px; right:2px; background:var(--accent2); color:#fff;
    font-size:9px; font-weight:700; min-width:14px; height:14px; line-height:14px;
    text-align:center; border-radius:7px; padding:0 3px; font-variant-numeric:tabular-nums; }
  .nm { text-decoration:underline; text-decoration-color:var(--line); }
  .nm:hover { text-decoration-color:var(--accent2); color:var(--accent2); }
  .eff { max-width:520px; white-space:pre-wrap; color:var(--dim); font-size:12.5px; }

  .mstars { color:#f4cf76; letter-spacing:0.5px; font-size:10px; text-shadow:0 1px 1px rgba(0,0,0,.4); }
  .mlvl { display:inline-flex; align-items:center; gap:4px; }
  .msub, .meff { display:none; }
  @media (orientation:portrait) {
    td.c-type, td.c-attr, td.c-race, td.c-kind, td.c-lv, td.c-atk, td.c-def, td.c-eff { display:none; }
    .msub { display:flex; align-items:center; flex-wrap:wrap; gap:4px 8px; margin-top:4px;
      font-size:11.5px; color:var(--dim); font-weight:400; }
    .meff { display:block; white-space:pre-wrap; overflow-wrap:anywhere; margin-top:5px;
      font-size:12px; line-height:1.4; color:var(--dim); font-weight:400; }
    td { padding:9px 8px; }
    td.thumb { padding:6px 4px 6px 10px; }
    td.thumb img { width:44px; height:44px; }
    td.lim { padding-right:10px; }
  }
</style>

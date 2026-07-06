<script>
  import { showDetail } from '../lib/stores/ui.svelte.js'
  import { add, sectionOf } from '../lib/stores/deck.svelte.js'
  import { showToast } from '../lib/stores/toast.svelte.js'
  import LimitBadge from './LimitBadge.svelte'

  let { card } = $props()

  const base = import.meta.env.VITE_DATA_BASE || import.meta.env.BASE_URL

  // Name/thumbnail -> details; else add to Main/Extra (Shift-click adds to Side).
  function rowClick(e) {
    if (e.target.closest('[data-details]')) {
      showDetail(card)
    } else {
      const r = add(card, e.shiftKey ? 'side' : sectionOf(card))
      if (!r.ok) showToast(r.reason)
    }
  }
</script>

<tr data-i={card.idx} onclick={rowClick} title="Click to add · Shift-click for Side">
  <td class="thumb" data-details><img class="pix" src={base + card.art} loading="lazy" alt="" /></td>
  <td class="name"><span class="nm" data-details>{card.name}</span></td>
  <td class="lim">{#if card.limit}<LimitBadge limit={card.limit} />{/if}</td>
  <td><span class="badge t-{card.cardType}">{card.cardType}</span></td>
  <td>{#if card.attribute}<span class="sub">{card.attribute}</span>{/if}</td>
  <td class="sub">{card.race || ''}</td>
  <td class="sub">{card.kind}</td>
  <td class="num">{card.level ?? ''}</td>
  <td class="num">{card.atk ?? ''}</td>
  <td class="num">{card.def ?? ''}</td>
  <td><div class="eff">{card.effect || ''}</div></td>
</tr>

<style>
  tr { border-bottom:1px solid var(--line); cursor:pointer; user-select:none; }
  tr:hover { background:var(--panel2); }
  td { padding:7px 10px; vertical-align:top; }
  td.name { font-weight:600; }
  td.num { text-align:right; font-variant-numeric:tabular-nums; color:var(--dim); }
  td.lim { width:1px; text-align:center; }
  td.thumb { padding:4px 4px 4px 12px; width:1px; }
  td.thumb img { width:34px; height:34px; object-fit:cover; image-rendering:pixelated;
    border-radius:4px; background:var(--panel2); display:block; }
  .nm { text-decoration:underline; text-decoration-color:var(--line); }
  .nm:hover { text-decoration-color:var(--accent2); color:var(--accent2); }
  .eff { max-width:520px; white-space:pre-wrap; color:var(--dim); font-size:12.5px; }
</style>

<script>
  import { showDetail } from '../lib/stores/ui.svelte.js'

  let { card } = $props()

  const base = import.meta.env.BASE_URL
</script>

<tr data-i={card.idx} onclick={() => showDetail(card)}>
  <td class="thumb"><img class="pix" src={base + card.art} loading="lazy" alt="" /></td>
  <td class="name">{card.name}</td>
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
  tr { border-bottom:1px solid var(--line); cursor:pointer; }
  tr:hover { background:var(--panel2); }
  td { padding:7px 10px; vertical-align:top; }
  td.name { font-weight:600; }
  td.num { text-align:right; font-variant-numeric:tabular-nums; color:var(--dim); }
  td.thumb { padding:4px 4px 4px 12px; width:1px; }
  td.thumb img { width:34px; height:34px; object-fit:cover; image-rendering:pixelated;
    border-radius:4px; background:var(--panel2); display:block; }
  .eff { max-width:520px; white-space:pre-wrap; color:var(--dim); font-size:12.5px; }
</style>

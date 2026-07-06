<script>
  import { data } from '../lib/stores/data.svelte.js'
  import { removeOne } from '../lib/stores/deck.svelte.js'
  import { rowAction } from '../lib/stores/ui.svelte.js'

  // rich: Deck-tab variant mirroring the Browse rows (type badge, meta line,
  // effect text); the compact form stays for the narrow Browse side panel.
  let { section, idx, count, rich = false } = $props()

  const base = import.meta.env.VITE_DATA_BASE || import.meta.env.BASE_URL
  const card = $derived(data.byIdx.get(idx))

  // Name/thumbnail open details; clicking anywhere else removes one copy.
  function click(e) {
    rowAction(e, card, () => removeOne(section, idx))
  }
  function keydown(e) {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault()
      removeOne(section, idx)
    }
  }

  const metaLine = $derived(
    card && card.cardType === 'Monster'
      ? [card.attribute, card.race, card.kind].filter(Boolean).join(' · ')
      : card?.icon || '',
  )
</script>

{#if card}
  <div class="de" class:rich role="button" tabindex="0" title="Remove one" data-i={idx} onclick={click} onkeydown={keydown}>
    <img class="pix thumb" data-details src={base + card.art} alt="" />
    {#if rich}
      <div class="body">
        <span class="rnm"><span class="nmt" data-details>{card.name}</span>{#if count > 1}<span class="ct">×{count}</span>{/if}</span>
        <div class="meta">
          <span class="badge t-{card.cardType}">{card.cardType}</span>
          {#if metaLine}<span>{metaLine}</span>{/if}
          {#if card.cardType === 'Monster'}<span>Lv {card.level ?? '—'} · {card.atk ?? '—'} / {card.def ?? '—'}</span>{/if}
        </div>
        {#if card.effect}<div class="eff">{card.effect}</div>{/if}
      </div>
    {:else}
      <span class="nm"><span class="nmt" data-details>{card.name}</span></span>
      {#if count > 1}<span class="ct">×{count}</span>{/if}
    {/if}
  </div>
{/if}

<style>
  .de {
    display: flex;
    align-items: center;
    gap: 7px;
    padding: 3px 8px;
    cursor: pointer;
    border-radius: 4px;
    user-select: none;
  }
  .de:hover {
    background: var(--panel2);
  }
  .thumb {
    width: 24px;
    height: 24px;
    object-fit: cover;
    border-radius: 3px;
    background: var(--panel2);
    flex-shrink: 0;
  }
  .nm {
    flex: 1;
    min-width: 0;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    font-size: 12.5px;
  }
  .nmt {
    text-decoration: underline;
    text-decoration-color: var(--line);
  }
  .nmt:hover {
    text-decoration-color: var(--accent2);
  }
  .ct {
    color: var(--dim);
    font-size: 12px;
    font-variant-numeric: tabular-nums;
  }

  .de.rich {
    align-items: flex-start;
    gap: 9px;
    padding: 7px 10px;
    border-bottom: 1px solid var(--line);
    border-radius: 0;
  }
  .de.rich .thumb {
    width: 34px;
    height: 34px;
  }
  .body {
    flex: 1;
    min-width: 0;
  }
  .rnm {
    display: flex;
    align-items: baseline;
    gap: 7px;
    font-size: 13px;
    font-weight: 600;
  }
  .meta {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 4px 8px;
    margin-top: 3px;
    font-size: 11.5px;
    color: var(--dim);
  }
  .eff {
    margin-top: 4px;
    white-space: pre-wrap;
    overflow-wrap: anywhere;
    font-size: 12px;
    line-height: 1.4;
    color: var(--dim);
  }

  @media (orientation: portrait) {
    .de {
      padding: 7px 10px;
    }
    .thumb {
      width: 30px;
      height: 30px;
    }
    .nm {
      font-size: 13px;
    }
    .de.rich .thumb {
      width: 44px;
      height: 44px;
    }
    /* Visible remove hint: on touch there is no hover state or title tooltip
       to reveal that tapping the row removes a copy. */
    .de::after {
      content: '−';
      color: var(--dim);
      font-size: 15px;
      line-height: 1;
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 2px 7px;
    }
  }
</style>

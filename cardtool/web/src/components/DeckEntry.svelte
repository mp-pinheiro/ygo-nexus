<script>
  import { data } from '../lib/stores/data.svelte.js'
  import { removeOne } from '../lib/stores/deck.svelte.js'
  import { rowAction } from '../lib/stores/ui.svelte.js'
  import { owned } from '../lib/stores/owned.svelte.js'
  import LimitBadge from './LimitBadge.svelte'

  // rich: Deck-tab variant mirroring the Browse rows (type badge, meta line,
  // effect text); detail: compact variant for the narrow side panel showing
  // type, stats, and a truncated effect; plain compact otherwise.
  let { section, idx, count, rich = false, detail = false } = $props()

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

  const invalid = $derived(owned.loaded && count > owned.copies(idx))

  const metaLine = $derived(
    card && card.cardType === 'Monster'
      ? [card.attribute, card.race, card.kind].filter(Boolean).join(' · ')
      : card?.icon || '',
  )
</script>

{#if card}
  <div class="de" class:rich class:detail class:invalid role="button" tabindex="0" title="Remove one" data-i={idx} onclick={click} onkeydown={keydown}>
    <img class="pix thumb" data-details src={base + card.art} alt="" />
    {#if rich}
      <div class="body">
        <span class="rnm"><span class="nmt" data-details>{card.name}</span>{#if card.limit}<LimitBadge limit={card.limit} size={16} />{/if}{#if count > 1}<span class="ct">×{count}</span>{/if}{#if owned.loaded}<span class="own" class:bad={invalid}>own {owned.copies(idx)}</span>{/if}</span>
        <div class="meta">
          <span class="badge t-{card.cardType}">{card.cardType}</span>
          {#if metaLine}<span>{metaLine}</span>{/if}
          {#if card.cardType === 'Monster'}
            <span class="rstars">
              {#if card.level != null}<span class="mstars" title="Level {card.level}">{'★'.repeat(Math.min(card.level, 12))}</span>{/if}
              {card.atk ?? '—'} / {card.def ?? '—'}
            </span>
          {/if}
        </div>
        {#if card.effect}<div class="eff">{card.effect}</div>{/if}
      </div>
    {:else if detail}
      <div class="dbody">
        <span class="nm"><span class="nmt" data-details>{card.name}</span>{#if count > 1}<span class="ct">×{count}</span>{/if}{#if owned.loaded}<span class="own" class:bad={invalid}>own {owned.copies(idx)}</span>{/if}</span>
        <div class="dmeta">
          <span class="badge t-{card.cardType}">{card.cardType}</span>
          {#if card.limit}<LimitBadge limit={card.limit} size={14} />{/if}
          {#if card.cardType === 'Monster'}
            {#if card.level != null}<span class="dstars" title="Lv {card.level}">{'★'.repeat(Math.min(card.level, 12))}</span>{/if}
            <span>{card.race || ''}</span>
            <span>{card.atk ?? '?'} / {card.def ?? '?'}</span>
          {:else if card.icon}
            <span>{card.icon}</span>
          {/if}
        </div>
        {#if card.effect}<div class="deff">{card.effect}</div>{/if}
      </div>
    {:else}
      <span class="nm"><span class="nmt" data-details>{card.name}</span></span>
      {#if count > 1}<span class="ct">×{count}</span>{/if}
      {#if owned.loaded}<span class="own" class:bad={invalid}>own {owned.copies(idx)}</span>{/if}
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
  .de.invalid {
    background: rgba(226, 59, 59, 0.08);
  }
  .de.invalid:hover {
    background: rgba(226, 59, 59, 0.14);
  }
  .own {
    font-size: 10px;
    color: var(--dim);
    margin-left: auto;
    font-variant-numeric: tabular-nums;
  }
  .own.bad {
    color: #e23b3b;
    font-weight: 600;
  }

  /* Detail mode: compact card info for the narrow side panel */
  .de.detail {
    align-items: flex-start;
    gap: 7px;
    padding: 5px 8px;
    border-bottom: 1px solid var(--line);
    border-radius: 0;
  }
  .dbody {
    flex: 1;
    min-width: 0;
  }
  .dbody .nm {
    display: flex;
    align-items: baseline;
    gap: 6px;
    font-size: 12.5px;
  }
  .dmeta {
    display: flex;
    align-items: center;
    gap: 5px;
    margin-top: 2px;
    font-size: 11px;
    color: var(--dim);
  }
  .dmeta .badge { font-size: 10px; padding: 0 5px; }
  .dstars { color:#f4cf76; font-size:9px; letter-spacing:0.5px; text-shadow:0 1px 1px rgba(0,0,0,.4); }
  .deff {
    margin-top: 2px;
    font-size: 11px;
    line-height: 1.35;
    color: var(--dim);
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
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
  .mstars { color:#f4cf76; letter-spacing:0.5px; font-size:10px; text-shadow:0 1px 1px rgba(0,0,0,.4); }
  .rstars { display:inline-flex; align-items:center; gap:3px; }
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

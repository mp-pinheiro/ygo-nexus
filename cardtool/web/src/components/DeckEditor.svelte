<script>
  // PR-1 deck-editor seam: read-only placeholder that proves the reactive deck
  // store renders. No add/remove UI or persistence yet (PR2). Card idx values
  // resolve to names through data.byIdx.
  import { deck, counts, validity } from '../lib/stores/deck.svelte.js'
  import { data } from '../lib/stores/data.svelte.js'

  // Section descriptors stay reactive: they read deck arrays + counts getters,
  // so they recompute whenever the deck store mutates.
  let sections = $derived([
    { label: 'Main', ids: deck.main, count: counts.main, limit: '40–60', bad: counts.main < 40 || counts.main > 60 },
    { label: 'Extra', ids: deck.extra, count: counts.extra, limit: '15', bad: counts.extra > 15 },
    { label: 'Side', ids: deck.side, count: counts.side, limit: '15', bad: counts.side > 15 },
  ])
</script>

<section class="deck">
  <header class="deck-head">
    <h2>Deck Editor</h2>
    <div class="summary">
      {#each sections as sec (sec.label)}
        <span class="stat" class:bad={sec.bad}>{sec.label} {sec.count}/{sec.limit}</span>
      {/each}
      <span class="validity" class:ok={validity.ok}>
        <span class="dot"></span>{validity.ok ? 'Valid' : 'Invalid'}
      </span>
    </div>
  </header>

  <div class="cols">
    {#each sections as sec (sec.label)}
      <div class="col">
        <div class="col-head">
          <span class="col-title">{sec.label}</span>
          <span class="cnt" class:bad={sec.bad}>{sec.count} / {sec.limit}</span>
        </div>
        {#if sec.ids.length}
          <ul>
            {#each sec.ids as idx, i (i)}
              <li>{data.byIdx.get(idx)?.name ?? `#${idx}`}</li>
            {/each}
          </ul>
        {:else}
          <p class="empty">No cards yet. Add cards from Browse (coming soon).</p>
        {/if}
      </div>
    {/each}
  </div>
</section>

<style>
  .deck {
    height: 100%;
    min-height: 0;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }

  .deck-head {
    flex: 0 0 auto;
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 10px 14px;
    padding: 12px 16px;
    background: var(--panel);
    border-bottom: 1px solid var(--line);
  }
  .deck-head h2 {
    margin: 0;
    font-size: 16px;
    color: var(--accent);
    white-space: nowrap;
  }

  .summary {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 6px;
    margin-left: auto;
  }
  .stat {
    background: var(--panel2);
    border: 1px solid var(--line);
    border-radius: 8px;
    padding: 4px 10px;
    font-size: 12px;
    color: var(--dim);
    white-space: nowrap;
  }
  .stat.bad {
    border-color: var(--trap);
    color: #e88bb8;
  }

  .validity {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-size: 12px;
    font-weight: 600;
    padding: 4px 10px;
    border-radius: 8px;
    border: 1px solid var(--line);
    color: #e88bb8;
    background: rgba(181, 66, 127, 0.12);
  }
  .validity.ok {
    color: #7fe6d3;
    background: rgba(29, 154, 138, 0.14);
    border-color: var(--spell);
  }
  .validity .dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: currentColor;
  }

  .cols {
    flex: 1 1 auto;
    min-height: 0;
    display: grid;
    grid-template-columns: 2fr 1fr 1fr;
    gap: 1px;
    background: var(--line);
  }

  .col {
    background: var(--bg);
    display: flex;
    flex-direction: column;
    min-height: 0;
    overflow-y: auto;
  }

  .col-head {
    position: sticky;
    top: 0;
    z-index: 1;
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    gap: 8px;
    padding: 8px 12px;
    background: var(--panel);
    border-bottom: 1px solid var(--line);
  }
  .col-title {
    font-size: 11px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--dim);
    font-weight: 600;
  }
  .cnt {
    font-size: 12px;
    color: var(--dim);
    font-variant-numeric: tabular-nums;
  }
  .cnt.bad {
    color: #e88bb8;
  }

  ul {
    margin: 0;
    padding: 6px 0;
    list-style: none;
  }
  li {
    padding: 6px 12px;
    font-size: 12.5px;
    border-bottom: 1px solid var(--line);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  li:hover {
    background: var(--panel2);
  }

  .empty {
    margin: 0;
    padding: 16px 12px;
    color: var(--dim);
    font-size: 12.5px;
  }

  @media (max-width: 640px) {
    .cols {
      grid-template-columns: 1fr;
    }
  }
</style>

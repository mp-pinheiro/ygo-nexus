<script>
  import { active, counts, validity, grouped } from '../lib/stores/deck.svelte.js'
  import DeckMenu from './DeckMenu.svelte'
  import DeckEntry from './DeckEntry.svelte'
  import { previewOn } from '../lib/stores/preview.svelte.js'

  const SECTIONS = [
    { key: 'main', label: 'Main', min: 40, max: 60 },
    { key: 'extra', label: 'Extra', max: 15 },
    { key: 'side', label: 'Side', max: 15 },
  ]
  const isBad = (s, n) => (s.min ? n < s.min || n > s.max : n > s.max)
  const limitText = (s) => (s.min ? `${s.min}–${s.max}` : `${s.max}`)
</script>

<section class="deck">
  <header class="deck-head">
    <h2>Deck Editor</h2>
    <DeckMenu />
    <div class="summary">
      {#each SECTIONS as s (s.key)}
        <span class="stat" class:bad={isBad(s, counts[s.key])}>{s.label} {counts[s.key]}/{limitText(s)}</span>
      {/each}
      <span class="validity" class:ok={validity.ok}><span class="dot"></span>{validity.ok ? 'Valid' : 'Invalid'}</span>
    </div>
  </header>

  {#if active.deck}
    <div class="cols" use:previewOn>
      {#each SECTIONS as s (s.key)}
        <div class="col">
          <div class="col-head">
            <span class="col-title">{s.label}</span>
            <span class="cnt" class:bad={isBad(s, counts[s.key])}>{counts[s.key]} / {limitText(s)}</span>
          </div>
          {#if counts[s.key]}
            <div class="col-list">
              {#each grouped(s.key) as row (row.idx)}
                <DeckEntry section={s.key} idx={row.idx} count={row.count} />
              {/each}
            </div>
          {:else}
            <p class="empty">Empty. Click cards in Browse to add.</p>
          {/if}
        </div>
      {/each}
    </div>
  {/if}
</section>

<style>
  .deck {
    flex: 1 1 auto;
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
  }
  .col-head {
    flex: 0 0 auto;
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
  .col-list {
    flex: 1 1 auto;
    min-height: 0;
    overflow-y: auto;
    padding: 6px 4px;
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

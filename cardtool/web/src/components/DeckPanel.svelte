<script>
  import { active, counts, validity, grouped } from '../lib/stores/deck.svelte.js'
  import { layout, toggleDeck, closeMobilePanels } from '../lib/stores/layout.svelte.js'
  import DeckMenu from './DeckMenu.svelte'
  import DeckEntry from './DeckEntry.svelte'
  import { previewOn } from '../lib/stores/preview.svelte.js'

  // sheet: rendered inside the mobile drawer, where the desktop collapse-to-rail
  // affordance makes no sense — the header button closes the drawer instead.
  let { sheet = false } = $props()

  const SECTIONS = [
    { key: 'main', label: 'Main', min: 40, max: 60 },
    { key: 'extra', label: 'Extra', max: 15 },
    { key: 'side', label: 'Side', max: 15 },
  ]
</script>

<div class="deckpanel" class:collapsed={!sheet && !layout.deck}>
  {#if sheet || layout.deck}
    <div class="dp-head">
      <span class="dp-title">Deck</span>
      <div class="dp-actions">
        <DeckMenu />
        {#if sheet}
          <button class="side-collapse" title="Close deck" aria-label="Close deck" onclick={closeMobilePanels}>×</button>
        {:else}
          <button class="side-collapse" title="Collapse deck" aria-label="Collapse deck" aria-expanded="true" onclick={toggleDeck}>›</button>
        {/if}
      </div>
    </div>
    {#if active.deck}
      <div class="dp-body" use:previewOn>
        {#each SECTIONS as s (s.key)}
          {@const n = counts[s.key]}
          <div class="sec">
            <div class="sec-head">
              <span class="sec-label">{s.label}</span>
              <span class="sec-count" class:bad={s.min ? n < s.min || n > s.max : n > s.max}>
                {n}{s.min ? `/${s.min}–${s.max}` : `/${s.max}`}
              </span>
            </div>
            {#each grouped(s.key) as row (row.idx)}
              <DeckEntry section={s.key} idx={row.idx} count={row.count} detail />
            {/each}
          </div>
        {/each}
        <div class="dp-valid" class:ok={validity.ok}>{validity.ok ? '✓ Legal deck' : 'Not legal yet'}</div>
      </div>
    {:else}
      <div class="dp-empty">No deck.</div>
    {/if}
  {:else}
    <button class="side-rail" title="Show deck" aria-label="Show deck" aria-expanded="false" onclick={toggleDeck}>
      <span class="chev" aria-hidden="true">‹</span>
      <span class="rail-label">Deck</span>
    </button>
  {/if}
</div>

<style>
  .deckpanel {
    border-left: 1px solid var(--line);
    display: flex;
    flex-direction: column;
    overflow: hidden;
    min-height: 0;
  }
  .dp-head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
    padding: 10px 12px;
    border-bottom: 1px solid var(--line);
    flex-shrink: 0;
  }
  .dp-title {
    font-weight: 600;
    color: var(--accent);
  }
  .dp-actions {
    display: flex;
    align-items: center;
    gap: 8px;
  }
  .dp-body {
    overflow-y: auto;
    padding: 8px 4px 4px;
    flex: 1;
    min-height: 0;
  }
  .sec {
    margin-bottom: 10px;
  }
  .sec-head {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    padding: 2px 8px 4px;
  }
  .sec-label {
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: var(--dim);
    font-weight: 600;
  }
  .sec-count {
    font-size: 12px;
    color: var(--dim);
    font-variant-numeric: tabular-nums;
  }
  .sec-count.bad {
    color: var(--danger);
  }
  .dp-valid {
    text-align: center;
    font-size: 12px;
    color: var(--dim);
    padding: 8px;
    border-top: 1px solid var(--line);
    flex-shrink: 0;
  }
  .dp-valid.ok {
    color: var(--ok);
  }
  .dp-empty {
    padding: 20px;
    color: var(--dim);
    text-align: center;
  }
</style>

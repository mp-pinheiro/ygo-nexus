<script>
  import { deckFilters, SORT_OPTIONS, hasActiveFilters, resetDeckFilters, toggleDeckSort } from '../lib/stores/deckFilters.svelte.js'
  import { toggleSet } from '../lib/stores/filters.svelte.js'
  import { activateKey } from '../lib/a11y.js'
</script>

<div class="dt">
  <input
    class="dq"
    type="search"
    placeholder="Search deck…"
    bind:value={deckFilters.q}
  />
  <div class="strip">
    {#each SORT_OPTIONS as opt (opt.k)}
      <button
        class="sbtn"
        class:active={deckFilters.sort === opt.k}
        onclick={() => toggleDeckSort(opt.k)}
      >
        {opt.label}
        {#if deckFilters.sort === opt.k}
          <span class="arrow">{deckFilters.dir === 1 ? '▲' : '▼'}</span>
        {/if}
      </button>
    {/each}
    <span class="sep" aria-hidden="true"></span>
    {#each ['Monster', 'Spell', 'Trap'] as t (t)}
      <span class="chip" class:on={deckFilters.types.has(t)} role="button" tabindex="0" aria-pressed={deckFilters.types.has(t)}
        onclick={() => toggleSet(deckFilters.types, t)} onkeydown={activateKey(() => toggleSet(deckFilters.types, t))}>{t}</span>
    {/each}
    {#if hasActiveFilters.value}
      <button class="clr" onclick={resetDeckFilters}>✕</button>
    {/if}
  </div>
</div>

<style>
  .dt {
    flex: 0 0 auto;
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 6px 12px;
    background: var(--panel);
    border-bottom: 1px solid var(--line);
  }
  .dq {
    width: 160px;
    flex-shrink: 0;
    background: var(--panel2);
    border: 1px solid var(--line);
    color: var(--txt);
    padding: 5px 9px;
    border-radius: 6px;
    font-size: 13px;
    font-family: inherit;
  }
  .dq:focus {
    outline: none;
    border-color: var(--accent2);
  }
  .strip {
    flex: 1;
    min-width: 0;
    display: flex;
    align-items: center;
    gap: 2px;
  }
  .sep {
    align-self: stretch;
    width: 1px;
    min-height: 16px;
    margin: 0 4px;
    background: var(--line);
  }
  .sbtn {
    appearance: none;
    background: none;
    border: 1px solid transparent;
    color: var(--dim);
    font-family: inherit;
    font-size: 11px;
    padding: 3px 7px;
    border-radius: 6px;
    cursor: pointer;
    white-space: nowrap;
    display: inline-flex;
    align-items: center;
    gap: 3px;
  }
  .sbtn:hover {
    color: var(--txt);
    background: var(--panel2);
  }
  .sbtn.active {
    color: var(--accent2);
    border-color: var(--accent2);
    background: rgba(79, 124, 255, 0.1);
  }
  .arrow {
    font-size: 8px;
  }
  .clr {
    appearance: none;
    background: var(--panel2);
    border: 1px solid var(--line);
    color: var(--dim);
    font-family: inherit;
    font-size: 12px;
    width: 22px;
    height: 22px;
    border-radius: 50%;
    cursor: pointer;
    display: inline-grid;
    place-items: center;
    flex-shrink: 0;
    line-height: 1;
    padding: 0;
  }
  .clr:hover {
    border-color: var(--accent2);
    color: var(--txt);
  }

  @media (orientation: portrait) {
    .dt {
      padding: 6px 10px;
      gap: 6px;
    }
    .dq {
      width: 0;
      flex: 1;
      min-width: 80px;
      font-size: 16px;
      padding: 7px 10px;
    }
    .strip {
      overflow-x: auto;
      scrollbar-width: none;
      flex-shrink: 0;
      flex: 0 0 auto;
    }
    .strip::-webkit-scrollbar {
      display: none;
    }
    .sbtn {
      font-size: 12px;
      padding: 4px 8px;
    }
  }
</style>

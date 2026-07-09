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
    flex: 0 0 auto;
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
      position: sticky;
      top: 0;
      z-index: 2;
      padding: 8px 10px;
      gap: 6px;
      overflow-x: auto;
      scrollbar-width: none;
    }
    .dt::-webkit-scrollbar {
      display: none;
    }
    .dq {
      width: 100px;
      flex: 0 0 auto;
      font-size: 14px;
      padding: 6px 10px;
      border-radius: 12px;
    }
    .sep {
      display: none;
    }
    .sbtn {
      background: var(--panel2);
      border: 1px solid var(--line);
      color: var(--dim);
      padding: 6px 11px;
      border-radius: 12px;
      font-size: 12px;
    }
    .sbtn.active {
      background: var(--accent2);
      border-color: var(--accent2);
      color: #fff;
    }
    .arrow {
      font-size: 10px;
    }
  }
</style>

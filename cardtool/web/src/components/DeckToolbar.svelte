<script>
  import { deckFilters, SORT_OPTIONS, hasActiveFilters, resetDeckFilters, toggleDeckSort } from '../lib/stores/deckFilters.svelte.js'
  import ChipGroup from './ChipGroup.svelte'
</script>

<div class="dt">
  <input
    class="dq"
    type="search"
    placeholder="Search deck…  dragon  -fusion  atk:>2000"
    bind:value={deckFilters.q}
  />
  <div class="sorts">
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
  </div>
  <div class="fchips">
    <ChipGroup title="" values={['Monster', 'Spell', 'Trap']} set={deckFilters.types} />
    {#if hasActiveFilters.value}
      <button class="clr" onclick={resetDeckFilters}>Clear</button>
    {/if}
  </div>
</div>

<style>
  .dt {
    flex: 0 0 auto;
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 8px;
    padding: 8px 12px;
    background: var(--panel);
    border-bottom: 1px solid var(--line);
  }
  .dq {
    flex: 1;
    min-width: 140px;
    background: var(--panel2);
    border: 1px solid var(--line);
    color: var(--txt);
    padding: 6px 10px;
    border-radius: 6px;
    font-size: 13px;
    font-family: inherit;
  }
  .dq:focus {
    outline: none;
    border-color: var(--accent2);
  }
  .sorts {
    display: flex;
    gap: 2px;
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
  .fchips {
    display: flex;
    align-items: center;
    gap: 5px;
  }
  .clr {
    appearance: none;
    background: none;
    border: 0;
    color: var(--dim);
    font-family: inherit;
    font-size: 11px;
    padding: 3px 7px;
    border-radius: 6px;
    cursor: pointer;
    text-decoration: underline;
    text-decoration-color: var(--line);
  }
  .clr:hover {
    color: var(--txt);
  }

  @media (orientation: portrait) {
    .dt {
      padding: 8px 10px;
      gap: 6px;
    }
    .dq {
      min-width: 0;
      font-size: 16px;
      padding: 8px 10px;
    }
    .sorts {
      overflow-x: auto;
      scrollbar-width: none;
      flex-wrap: nowrap;
    }
    .sorts::-webkit-scrollbar {
      display: none;
    }
    .sbtn {
      font-size: 12px;
      padding: 5px 9px;
    }
    .fchips {
      overflow-x: auto;
      scrollbar-width: none;
      flex-wrap: nowrap;
    }
    .fchips::-webkit-scrollbar {
      display: none;
    }
  }
</style>

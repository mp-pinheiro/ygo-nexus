<script>
  import { COLS, CAP } from '../lib/cards.js'
  import { filters } from '../lib/stores/filters.svelte.js'
  import { results } from '../lib/stores/results.svelte.js'
  import { previewOn } from '../lib/stores/preview.svelte.js'
  import CardRow from './CardRow.svelte'

  // Header click: toggle direction when re-sorting the active column, else asc.
  // Direction is computed against the OLD sort key before it is reassigned.
  function sortBy(k) {
    filters.dir = filters.sort === k ? -filters.dir : 1
    filters.sort = k
  }

  const indicator = (k) => (filters.sort === k ? (filters.dir === 1 ? '▲' : '▼') : '–')
</script>

<main>
  <table>
    <thead>
      <tr>
        <th class="thumb-h"></th>
        {#each COLS as col (col.k)}
          <th class:sorted={filters.sort === col.k} onclick={() => sortBy(col.k)}>
            {col.label} <span class="ind">{indicator(col.k)}</span>
          </th>
        {/each}
      </tr>
    </thead>
    <tbody use:previewOn>
      {#each results.list.slice(0, CAP) as card (card.idx)}
        <CardRow {card} />
      {/each}
    </tbody>
  </table>
  <div class="more">
    {#if results.count > CAP}Showing first {CAP} — refine your search to see the rest.{/if}
  </div>
</main>

<style>
  main { overflow:auto; }
  table { width:100%; border-collapse:collapse; }
  thead th { position:sticky; top:0; background:var(--panel); text-align:left;
    padding:8px 10px; font-size:11px; letter-spacing:.05em; text-transform:uppercase;
    color:var(--dim); border-bottom:1px solid var(--line); cursor:pointer; white-space:nowrap; }
  thead th:hover { color:var(--accent); }
  thead th.sorted { color:var(--accent); }
  .ind { color:var(--dim); font-size:10px; margin-left:2px; }
  th.sorted .ind { color:var(--accent); }
  .thumb-h { width:1px; }
  .more { padding:16px; text-align:center; color:var(--dim); }
</style>

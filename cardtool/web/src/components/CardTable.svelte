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
  <!-- Mobile-only sort strip: the narrow layout hides most table columns, so
       the thead is swapped for this scrollable strip to keep every sort key
       reachable. -->
  <div class="sortbar" role="toolbar" aria-label="Sort by">
    <span class="sb-lbl">Sort</span>
    {#each COLS as col (col.k)}
      <button class="sb" class:on={filters.sort === col.k} onclick={() => sortBy(col.k)}>
        {col.label}{#if filters.sort === col.k}<span class="sb-ind">{filters.dir === 1 ? '▲' : '▼'}</span>{/if}
      </button>
    {/each}
  </div>
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

  .sortbar { display:none; }
  @media (orientation:portrait) {
    thead { display:none; }
    .sortbar { position:sticky; top:0; z-index:2; display:flex; align-items:center;
      gap:6px; padding:8px 10px; background:var(--panel); border-bottom:1px solid var(--line);
      overflow-x:auto; scrollbar-width:none; }
    .sortbar::-webkit-scrollbar { display:none; }
    .sb-lbl { flex:0 0 auto; color:var(--dim); font-size:11px; letter-spacing:.05em;
      text-transform:uppercase; }
    .sb { flex:0 0 auto; display:inline-flex; align-items:center; gap:4px;
      background:var(--panel2); border:1px solid var(--line); color:var(--dim);
      padding:6px 11px; border-radius:12px; cursor:pointer; font-size:12px; font-family:inherit; }
    .sb.on { background:var(--accent2); border-color:var(--accent2); color:#fff; }
    .sb-ind { font-size:10px; }
    .more { padding:12px; font-size:12px; }
  }
</style>

<script>
  import { SEARCH_FIELDS } from '../lib/cards.js'
  import { filters, searchIn, setAllSearchIn } from '../lib/stores/filters.svelte.js'
  import { results } from '../lib/stores/results.svelte.js'
  import { data } from '../lib/stores/data.svelte.js'
</script>

<header>
  <h1>◆ Nexus Revival</h1>
  <!-- Direct bind replaces the monolith's 90ms debounce; Svelte's keyed diffing
       keeps re-renders cheap. match() trims/lowercases filters.q internally. -->
  <input id="q" type="search" placeholder="Search…  (multiple words = AND)" autofocus bind:value={filters.q} />
  <span id="count">{results.count.toLocaleString()} / {data.count.toLocaleString()} cards</span>
  <div class="searchin">
    <span class="lbl">Search in:</span>
    {#each SEARCH_FIELDS as [key, label] (key)}
      <span class="chip" class:on={searchIn[key]} onclick={() => (searchIn[key] = !searchIn[key])}>{label}</span>
    {/each}
    <span class="chip act" onclick={() => setAllSearchIn(true)}>all</span>
    <span class="chip act" onclick={() => setAllSearchIn(false)}>none</span>
  </div>
</header>

<style>
  header {
    flex: 0 0 auto;
    background: var(--panel);
    border-bottom: 1px solid var(--line);
    padding: 10px 16px;
    display: flex;
    align-items: center;
    gap: 12px 14px;
    flex-wrap: wrap;
  }
  header h1 {
    font-size: 16px;
    margin: 0;
    color: var(--accent);
    white-space: nowrap;
  }
  #q {
    flex: 1;
    min-width: 220px;
    background: var(--panel2);
    border: 1px solid var(--line);
    color: var(--txt);
    padding: 9px 12px;
    border-radius: 8px;
    font-size: 15px;
  }
  #q:focus {
    outline: none;
    border-color: var(--accent2);
  }
  #count {
    color: var(--dim);
    font-size: 13px;
    white-space: nowrap;
  }
  .searchin {
    flex-basis: 100%;
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 6px;
  }
  .searchin .lbl {
    color: var(--dim);
    font-size: 12px;
  }
</style>

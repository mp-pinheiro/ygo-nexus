<script>
  import { SEARCH_FIELDS } from '../lib/cards.js'
  import { filters, searchIn, setAllSearchIn } from '../lib/stores/filters.svelte.js'
  import { results } from '../lib/stores/results.svelte.js'
  import { data } from '../lib/stores/data.svelte.js'
  import { activateKey, focusOnMount } from '../lib/a11y.js'

  let showHelp = $state(false)
</script>

<header>
  <h1>◆ Nexus Revival</h1>
  <!-- Direct bind replaces the monolith's 90ms debounce; Svelte's keyed diffing
       keeps re-renders cheap. parseQuery() lowercases filters.q internally. -->
  <input id="q" type="search" placeholder={'Search…  dragon -fusion   "blue-eyes" or destroy'} use:focusOnMount bind:value={filters.q} />
  <span id="count">{results.count.toLocaleString()} / {data.count.toLocaleString()} cards</span>
  <div class="searchin">
    <span class="lbl">Search in:</span>
    {#each SEARCH_FIELDS as [key, label] (key)}
      <span class="chip" class:on={searchIn[key]} role="button" tabindex="0" aria-pressed={searchIn[key]}
        onclick={() => (searchIn[key] = !searchIn[key])}
        onkeydown={activateKey(() => (searchIn[key] = !searchIn[key]))}>{label}</span>
    {/each}
    <span class="divider" aria-hidden="true"></span>
    <button type="button" class="ghost" onclick={() => setAllSearchIn(true)}>all</button>
    <button type="button" class="ghost" onclick={() => setAllSearchIn(false)}>none</button>
    <button type="button" class="help-toggle" class:on={showHelp} aria-expanded={showHelp}
      onclick={() => (showHelp = !showHelp)}><span class="q" aria-hidden="true">?</span>syntax</button>
  </div>
  {#if showHelp}
    <dl class="qhelp">
      <dt><code>dragon fusion</code></dt><dd>both words (AND)</dd>
      <dt><code>dragon or destroy</code></dt><dd>either word (OR)</dd>
      <dt><code>-token</code></dt><dd>exclude</dd>
      <dt><code>"blue-eyes white"</code></dt><dd>exact phrase</dd>
      <dt><code>name:dragon</code> <code>attr:dark</code> <code>type:spell</code> <code>kind:fusion</code></dt><dd>match one field</dd>
      <dt><code>atk:&gt;2000</code> <code>lv:4..8</code> <code>def:&lt;=1000</code></dt><dd>numeric compare</dd>
    </dl>
  {/if}
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
  /* Divider sets the field toggles apart from the bulk-select actions. */
  .searchin .divider {
    align-self: stretch;
    width: 1px;
    min-height: 16px;
    margin: 0 3px;
    background: var(--line);
  }
  .searchin .ghost {
    appearance: none;
    background: none;
    border: 0;
    color: var(--dim);
    font-family: inherit;
    font-size: 12px;
    padding: 3px 7px;
    border-radius: 8px;
    cursor: pointer;
  }
  .searchin .ghost:hover {
    color: var(--txt);
    background: var(--panel2);
  }
  /* Help toggle is anchored to the far right, away from the field toggles. */
  .searchin .help-toggle {
    appearance: none;
    margin-left: auto;
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: var(--panel2);
    border: 1px solid var(--line);
    color: var(--dim);
    font-family: inherit;
    font-size: 12px;
    padding: 3px 11px 3px 7px;
    border-radius: 12px;
    cursor: pointer;
  }
  .searchin .help-toggle:hover,
  .searchin .help-toggle.on {
    border-color: var(--accent2);
    color: var(--txt);
  }
  .searchin .help-toggle.on {
    background: rgba(79, 124, 255, 0.14);
  }
  .searchin .help-toggle .q {
    display: inline-grid;
    place-items: center;
    width: 15px;
    height: 15px;
    border-radius: 50%;
    background: var(--line);
    color: var(--txt);
    font-size: 11px;
    font-weight: 700;
  }
  .searchin .help-toggle.on .q {
    background: var(--accent2);
    color: #fff;
  }
  .qhelp {
    flex-basis: 100%;
    display: grid;
    grid-template-columns: auto 1fr;
    align-items: center;
    gap: 5px 14px;
    margin: 0;
    font-size: 12px;
    color: var(--dim);
  }
  .qhelp dt {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
  }
  .qhelp dd {
    margin: 0;
  }
  .qhelp code {
    background: var(--panel2);
    border: 1px solid var(--line);
    border-radius: 4px;
    padding: 1px 6px;
    color: var(--txt);
    font-family: ui-monospace, monospace;
  }

  @media (orientation: portrait) {
    header {
      padding: 8px 10px;
      gap: 8px;
      /* The sticky sort strip sits directly below with the same background;
         the divider line between the two bars reads as a stray gap. */
      border-bottom: 0;
    }
    header h1 {
      display: none;
    }
    #q {
      min-width: 0;
      /* 16px stops iOS Safari from auto-zooming the page on focus. */
      font-size: 16px;
      padding: 8px 12px;
    }
    #count {
      font-size: 11px;
    }
    .searchin {
      flex-wrap: nowrap;
      overflow-x: auto;
      scrollbar-width: none;
      padding-bottom: 2px;
    }
    .searchin::-webkit-scrollbar {
      display: none;
    }
    .qhelp {
      font-size: 11px;
    }
  }
</style>

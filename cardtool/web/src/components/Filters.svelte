<script>
  // Sidebar composing the facet chip groups, numeric ranges, the owned-only
  // toggle, and the Reset button (monolith buildFilters/reset). The facet lists
  // (races/kinds/icons) come from the loaded data store.
  import { ATTRS } from '../lib/cards.js'
  import { data } from '../lib/stores/data.svelte.js'
  import { filters, reset } from '../lib/stores/filters.svelte.js'
  import { owned, importSave, clearSave } from '../lib/stores/owned.svelte.js'
  import { layout, toggleFilters, closeMobilePanels } from '../lib/stores/layout.svelte.js'
  import ChipGroup from './ChipGroup.svelte'
  import RangeGroup from './RangeGroup.svelte'

  let { sheet = false } = $props()

  let fileInput = $state()

  function onFile(e) {
    const file = e.target.files?.[0]
    if (file) importSave(file)
    if (fileInput) fileInput.value = ''
  }

  function removeSave() {
    clearSave()
  }
</script>

<aside class:collapsed={!sheet && !layout.filters}>
  {#if sheet || layout.filters}
    <div class="side-head">
      <h2 class="side-title">Filters</h2>
      {#if sheet}
        <button class="side-collapse" title="Close filters" aria-label="Close filters" onclick={closeMobilePanels}>×</button>
      {:else}
        <button class="side-collapse" title="Collapse filters" aria-label="Collapse filters" aria-expanded="true" onclick={toggleFilters}>‹</button>
      {/if}
    </div>
    <ChipGroup title="Card type" values={['Monster', 'Spell', 'Trap']} set={filters.types} />
    <ChipGroup title="Banlist" values={['Forbidden', 'Limited', 'Semi-Limited', 'Unlimited']} set={filters.limits} />
    <ChipGroup title="Attribute" values={ATTRS} set={filters.attrs} />
    <RangeGroup title="Level" keyBase="lv" />
    <RangeGroup title="ATK" keyBase="atk" />
    <RangeGroup title="DEF" keyBase="def" />
    <ChipGroup title="Monster type" values={data.races} set={filters.races} />
    <ChipGroup title="Kind" values={data.kinds} set={filters.kinds} />
    <ChipGroup title="Spell/Trap icon" values={data.icons} set={filters.icons} />

    <div class="fg">
      <h3>Collection</h3>
      {#if owned.loaded}
        <p class="save-info">Save loaded <span class="owned-count">{owned.total} copies</span></p>
        <button class="save-action remove" onclick={removeSave}>Show all (remove save)</button>
      {:else}
        <button class="save-action" onclick={() => fileInput?.click()}>Import save file</button>
        <input bind:this={fileInput} type="file" accept=".sav" hidden onchange={onFile} />
      {/if}
      {#if owned.error}
        <p class="save-err">{owned.error}</p>
      {/if}
    </div>

    <button class="reset" onclick={reset}>Reset filters</button>
  {:else}
    <button class="side-rail" title="Show filters" aria-label="Show filters" aria-expanded="false" onclick={toggleFilters}>
      <span class="chev" aria-hidden="true">›</span>
      <span class="rail-label">Filters</span>
    </button>
  {/if}
</aside>

<style>
  /* Structural sidebar CSS (monolith .fg/.toggle/button.reset); aside and the
     .chip* classes stay global in app.css. */
  aside.collapsed { padding:0; overflow:hidden; }
  .side-head { display:flex; align-items:center; justify-content:space-between; margin-bottom:14px; }
  .side-title { margin:0; font-size:13px; font-weight:600; color:var(--accent); }
  .fg { margin-bottom:16px; }
  .fg h3 { margin:0 0 7px; font-size:11px; letter-spacing:.08em; text-transform:uppercase;
    color:var(--dim); font-weight:600; }
  button.reset { width:100%; background:var(--panel2); border:1px solid var(--line);
    color:var(--txt); padding:8px; border-radius:8px; cursor:pointer; }
  button.reset:hover { border-color:var(--accent); color:var(--accent); }
  .save-info { margin:0 0 4px; font-size:12px; color:var(--dim); display:flex; align-items:center; gap:6px; }
  .owned-count { margin-left:auto; font-size:11px; color:var(--accent); font-variant-numeric:tabular-nums; }
  .save-action { background:var(--panel2); border:1px solid var(--line); color:var(--txt);
    padding:6px 10px; border-radius:8px; cursor:pointer; font-size:12px; width:100%; margin-top:6px; }
  .save-action:hover { border-color:var(--accent); color:var(--accent); }
  .save-action.remove { color:var(--dim); }
  .save-action.remove:hover { border-color:#e23b3b; color:#e23b3b; }
  .save-err { margin:6px 0 0; font-size:11px; color:var(--err); }
</style>

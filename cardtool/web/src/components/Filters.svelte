<script>
  // Sidebar composing the facet chip groups, numeric ranges, the disabled
  // "Owned only" stub, and the Reset button (monolith buildFilters/reset). The
  // facet lists (races/kinds/icons) come from the loaded data store.
  import { ATTRS } from '../lib/cards.js'
  import { data } from '../lib/stores/data.svelte.js'
  import { filters, reset } from '../lib/stores/filters.svelte.js'
  import ChipGroup from './ChipGroup.svelte'
  import RangeGroup from './RangeGroup.svelte'
</script>

<aside>
  <ChipGroup title="Card type" values={['Monster', 'Spell', 'Trap']} set={filters.types} />
  <ChipGroup title="Attribute" values={ATTRS} set={filters.attrs} />
  <RangeGroup title="Level" keyBase="lv" />
  <RangeGroup title="ATK" keyBase="atk" />
  <RangeGroup title="DEF" keyBase="def" />
  <ChipGroup title="Monster type" values={data.races} set={filters.races} />
  <ChipGroup title="Kind" values={data.kinds} set={filters.kinds} />
  <ChipGroup title="Spell/Trap icon" values={data.icons} set={filters.icons} />

  <div class="fg">
    <h3>Collection</h3>
    <label class="toggle disabled" title="Import a save file to enable (coming soon)">
      <input type="checkbox" disabled /> Owned only
    </label>
  </div>

  <button class="reset" onclick={reset}>Reset filters</button>
</aside>

<style>
  /* Structural sidebar CSS (monolith .fg/.toggle/button.reset); aside and the
     .chip* classes stay global in app.css. */
  .fg { margin-bottom:16px; }
  .fg h3 { margin:0 0 7px; font-size:11px; letter-spacing:.08em; text-transform:uppercase;
    color:var(--dim); font-weight:600; }
  button.reset { width:100%; background:var(--panel2); border:1px solid var(--line);
    color:var(--txt); padding:8px; border-radius:8px; cursor:pointer; }
  button.reset:hover { border-color:var(--accent); color:var(--accent); }
  label.toggle { display:flex; align-items:center; gap:8px; color:var(--dim); cursor:pointer; }
  label.toggle.disabled { opacity:.5; cursor:not-allowed; }
</style>

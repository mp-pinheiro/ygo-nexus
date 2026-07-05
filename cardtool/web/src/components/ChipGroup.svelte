<script>
  // A titled group of toggle chips backed by a filters SvelteSet. Membership
  // drives the .on class; clicking toggles the value in place (reactive set →
  // results re-derive automatically, replacing the monolith's render() call).
  import { toggleSet } from '../lib/stores/filters.svelte.js'
  import { activateKey } from '../lib/a11y.js'

  let { title, values, set } = $props()
</script>

<div class="fg">
  <h3>{title}</h3>
  <div class="chips">
    {#each values as v (v)}
      <span class="chip" class:on={set.has(v)} role="button" tabindex="0" aria-pressed={set.has(v)}
        onclick={() => toggleSet(set, v)} onkeydown={activateKey(() => toggleSet(set, v))}>{v}</span>
    {/each}
  </div>
</div>

<style>
  /* Structural sidebar CSS (monolith .fg/.chips); .chip* stay global in app.css. */
  .fg { margin-bottom:16px; }
  .fg h3 { margin:0 0 7px; font-size:11px; letter-spacing:.08em; text-transform:uppercase;
    color:var(--dim); font-weight:600; }
  .chips { display:flex; flex-wrap:wrap; gap:5px; }
</style>

<script>
  // Min/max numeric range for a filter key pair (keyBase+'Min' / keyBase+'Max').
  // The fields are kept as raw strings (matching the monolith and the filters
  // store's "" contract): we write input.value directly rather than bind:value,
  // because Svelte coerces an empty number input to null, which would break
  // inRange()'s "" checks. value= reflects the store so Reset clears the inputs.
  import { filters } from '../lib/stores/filters.svelte.js'

  let { title, keyBase } = $props()
</script>

<div class="fg">
  <h3>{title}</h3>
  <div class="range">
    <input
      type="number"
      placeholder="min"
      value={filters[keyBase + 'Min']}
      oninput={(e) => (filters[keyBase + 'Min'] = e.currentTarget.value)}
    />
    <span>–</span>
    <input
      type="number"
      placeholder="max"
      value={filters[keyBase + 'Max']}
      oninput={(e) => (filters[keyBase + 'Max'] = e.currentTarget.value)}
    />
  </div>
</div>

<style>
  /* Structural sidebar CSS (monolith .fg/.range). */
  .fg { margin-bottom:16px; }
  .fg h3 { margin:0 0 7px; font-size:11px; letter-spacing:.08em; text-transform:uppercase;
    color:var(--dim); font-weight:600; }
  .range { display:flex; align-items:center; gap:6px; }
  .range input { width:100%; background:var(--panel2); border:1px solid var(--line);
    color:var(--txt); padding:5px 7px; border-radius:6px; }
  .range span { color:var(--dim); }
</style>

<script>
  import { data } from '../lib/stores/data.svelte.js'
  import { removeOne } from '../lib/stores/deck.svelte.js'
  import { showDetail } from '../lib/stores/ui.svelte.js'

  let { section, idx, count } = $props()

  const base = import.meta.env.BASE_URL
  const card = $derived(data.byIdx.get(idx))

  // The underlined name opens details; clicking anywhere else removes one copy.
  function click(e) {
    if (e.target.closest('[data-details]')) showDetail(card)
    else removeOne(section, idx)
  }
  function keydown(e) {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault()
      removeOne(section, idx)
    }
  }
</script>

{#if card}
  <div class="de" role="button" tabindex="0" title="Remove one" data-i={idx} onclick={click} onkeydown={keydown}>
    <img class="pix thumb" src={base + card.art} alt="" />
    <span class="nm"><span class="nmt" data-details>{card.name}</span></span>
    {#if count > 1}<span class="ct">×{count}</span>{/if}
  </div>
{/if}

<style>
  .de {
    display: flex;
    align-items: center;
    gap: 7px;
    padding: 3px 8px;
    cursor: pointer;
    border-radius: 4px;
    user-select: none;
  }
  .de:hover {
    background: var(--panel2);
  }
  .thumb {
    width: 24px;
    height: 24px;
    object-fit: cover;
    border-radius: 3px;
    background: var(--panel2);
    flex-shrink: 0;
  }
  .nm {
    flex: 1;
    min-width: 0;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    font-size: 12.5px;
  }
  .nmt {
    text-decoration: underline;
    text-decoration-color: var(--line);
  }
  .nmt:hover {
    text-decoration-color: var(--accent2);
  }
  .ct {
    color: var(--dim);
    font-size: 12px;
    font-variant-numeric: tabular-nums;
  }
</style>

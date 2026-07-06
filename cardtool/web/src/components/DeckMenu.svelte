<script>
  import { deck, createDeck, renameDeck, duplicateDeck, deleteDeck, setActive } from '../lib/stores/deck.svelte.js'

  let open = $state(false)
  let dmEl = $state()
  let alignLeft = $state(false)
  const activeDeck = $derived(deck.list.find((d) => d.id === deck.activeId) ?? null)

  // The menu is right-aligned to the button; when the button sits near the left
  // viewport edge (Deck Editor header on phones) that pushes the menu off-screen,
  // so flip to left alignment when a right-aligned menu would clip.
  function toggle() {
    if (!open && dmEl) alignLeft = dmEl.getBoundingClientRect().right - 180 < 8
    open = !open
  }

  function rename() {
    const name = prompt('Rename deck', activeDeck?.name)
    if (name != null) renameDeck(deck.activeId, name)
    open = false
  }
  function del() {
    if (activeDeck && confirm(`Delete "${activeDeck.name}"?`)) deleteDeck(deck.activeId)
    open = false
  }
</script>

<div class="dm" bind:this={dmEl}>
  <button type="button" class="deckbtn" aria-haspopup="menu" aria-expanded={open} onclick={toggle}>
    {activeDeck?.name ?? 'No deck'} ▾
  </button>
  {#if open}
    <div class="menu" class:aleft={alignLeft} role="menu">
      {#each deck.list as d (d.id)}
        <button type="button" class="mi" class:on={d.id === deck.activeId} role="menuitem" onclick={() => { setActive(d.id); open = false }}>{d.name}</button>
      {/each}
      <div class="sep"></div>
      <button type="button" class="mi" role="menuitem" onclick={() => { createDeck(); open = false }}>+ New deck</button>
      <button type="button" class="mi" role="menuitem" onclick={rename}>Rename</button>
      <button type="button" class="mi" role="menuitem" onclick={() => { duplicateDeck(deck.activeId); open = false }}>Duplicate</button>
      <button type="button" class="mi danger" role="menuitem" onclick={del}>Delete</button>
    </div>
  {/if}
</div>

<style>
  .dm {
    position: relative;
  }
  .deckbtn {
    background: var(--panel2);
    border: 1px solid var(--line);
    color: var(--txt);
    padding: 5px 10px;
    border-radius: 7px;
    cursor: pointer;
    font-size: 12.5px;
    max-width: 100%;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  .deckbtn:hover {
    border-color: var(--accent);
  }
  .menu {
    position: absolute;
    right: 0;
    top: calc(100% + 4px);
    z-index: 30;
    min-width: 180px;
    max-width: calc(100vw - 16px);
    background: var(--panel);
    border: 1px solid var(--line);
    border-radius: 8px;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.55);
    padding: 4px;
    display: flex;
    flex-direction: column;
    max-height: 60vh;
    overflow-y: auto;
  }
  .menu.aleft {
    right: auto;
    left: 0;
  }
  .mi {
    text-align: left;
    background: none;
    border: 0;
    color: var(--txt);
    padding: 6px 9px;
    border-radius: 5px;
    cursor: pointer;
    font-size: 12.5px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  .mi:hover {
    background: var(--panel2);
  }
  .mi.on {
    color: var(--accent);
  }
  .mi.danger:hover {
    color: #ff8a8a;
  }
  .sep {
    height: 1px;
    background: var(--line);
    margin: 4px 2px;
  }
  @media (orientation: portrait) {
    .deckbtn {
      padding: 8px 12px;
      font-size: 13px;
    }
    .mi {
      padding: 10px 12px;
      font-size: 13.5px;
    }
  }
</style>

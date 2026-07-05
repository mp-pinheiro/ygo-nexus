<script>
  import { onMount } from 'svelte'
  import { data, loadDB } from './lib/stores/data.svelte.js'
  import { nav } from './lib/stores/nav.svelte.js'
  import { escape } from './lib/stores/ui.svelte.js'
  import SearchBar from './components/SearchBar.svelte'
  import Filters from './components/Filters.svelte'
  import CardTable from './components/CardTable.svelte'
  import HoverPreview from './components/HoverPreview.svelte'
  import CardDetail from './components/CardDetail.svelte'
  import ZoomOverlay from './components/ZoomOverlay.svelte'
  import PackPopover from './components/PackPopover.svelte'
  import DeckEditor from './components/DeckEditor.svelte'
  import DeckPanel from './components/DeckPanel.svelte'
  import Toast from './components/Toast.svelte'
  import { loadDecks } from './lib/stores/deck.svelte.js'

  // Load the card DB once; the whole app stays gated on data.loaded until then.
  onMount(() => {
    loadDB()
    loadDecks()
  })
</script>

<!-- Escape cascade (ui.escape): packpop -> zoom -> detail -> clear search. -->
<svelte:window
  onkeydown={(e) => {
    if (e.key === 'Escape') escape()
  }}
/>

{#if !data.loaded}
  <div class="gate">
    {#if data.error}
      <p class="err">Failed to load cards: {data.error}</p>
    {:else}
      <p>Loading…</p>
    {/if}
  </div>
{:else}
  <nav class="viewbar">
    <button class:active={nav.view === 'browse'} onclick={() => (nav.view = 'browse')}>Browse</button>
    <button class:active={nav.view === 'deck'} onclick={() => (nav.view = 'deck')}>Deck</button>
  </nav>

  {#if nav.view === 'browse'}
    <!-- Filters renders its own <aside>, CardTable its own <main>, so they drop
         straight into the .layout grid columns — the exact monolith DOM. -->
    <SearchBar />
    <div class="layout">
      <Filters />
      <CardTable />
      <DeckPanel />
    </div>
  {:else}
    <div class="view"><DeckEditor /></div>
  {/if}
  <HoverPreview />
  <CardDetail />
  <ZoomOverlay />
  <PackPopover />
  <Toast />
{/if}

<style>
  /* Top-level Browse|Deck toggle bar (new to the component app). */
  .viewbar {
    flex: 0 0 auto;
    display: flex;
    gap: 6px;
    padding: 8px 16px;
    background: var(--panel);
    border-bottom: 1px solid var(--line);
  }
  .viewbar button {
    background: var(--panel2);
    border: 1px solid var(--line);
    color: var(--dim);
    padding: 5px 16px;
    border-radius: 8px;
    cursor: pointer;
    font-size: 13px;
    font-family: inherit;
  }
  .viewbar button:hover {
    border-color: var(--accent2);
    color: var(--txt);
  }
  .viewbar button.active {
    background: var(--accent2);
    border-color: var(--accent2);
    color: #fff;
  }

  /* Fills the remaining column height so DeckEditor's height:100% resolves. */
  .view {
    flex: 1 1 auto;
    min-height: 0;
    display: flex;
    flex-direction: column;
  }

  .gate {
    flex: 1 1 auto;
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--dim);
  }
  .gate .err {
    color: #e88bb8;
  }
</style>

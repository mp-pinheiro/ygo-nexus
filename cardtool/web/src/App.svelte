<script>
  import { onMount } from 'svelte'
  import { fade, fly } from 'svelte/transition'
  import { data, loadDB } from './lib/stores/data.svelte.js'
  import { nav, initPopState } from './lib/stores/nav.svelte.js'
  import { media } from './lib/stores/media.svelte.js'
  import { layout, openMobileFilters, openMobileDeck, closeMobilePanels } from './lib/stores/layout.svelte.js'
  import { filters } from './lib/stores/filters.svelte.js'
  import { counts } from './lib/stores/deck.svelte.js'
  import { escape, ui, closeDetail } from './lib/stores/ui.svelte.js'
  import { theme, toggleTheme } from './lib/stores/theme.svelte.js'
  import { clickSelf } from './lib/a11y.js'

  let touchStartX = 0
  let touchStartY = 0
  let touchStartTime = 0

  function onTouchStart(e) {
    touchStartX = e.touches[0].clientX
    touchStartY = e.touches[0].clientY
    touchStartTime = Date.now()
  }

  function onTouchEnd(e) {
    if (!media.mobile || nav.view !== 'browse') return
    if (layout.mFilters || layout.mDeck) return
    if (ui.detailIdx != null) return
    const dx = e.changedTouches[0].clientX - touchStartX
    const dy = e.changedTouches[0].clientY - touchStartY
    const dt = Date.now() - touchStartTime
    if (dt > 400 || Math.abs(dy) > Math.abs(dx) * 0.7) return
    const minSwipe = 60
    if (dx > minSwipe) openMobileFilters()
    else if (dx < -minSwipe) openMobileDeck()
  }
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
    initPopState((tag) => {
      if (tag === 'detail') { ui.detailIdx = null; ui.packpop = null }
      else if (tag === 'drawer') { layout.mFilters = false; layout.mDeck = false }
    })
  })

  // Crossing to desktop unmounts the drawer DOM but not its flags; clear them
  // so a drawer doesn't spring back open when the viewport returns to mobile
  // (phone rotation) and Escape isn't consumed by an invisible drawer.
  $effect(() => {
    if (!media.mobile) closeMobilePanels()
  })

  // Active-filter tally for the mobile Filters button badge; q is excluded
  // because the search box is always visible.
  const fcount = $derived(
    filters.types.size +
      filters.limits.size +
      filters.attrs.size +
      filters.races.size +
      filters.kinds.size +
      filters.icons.size +
      (filters.lvMin !== '' || filters.lvMax !== '' ? 1 : 0) +
      (filters.atkMin !== '' || filters.atkMax !== '' ? 1 : 0) +
      (filters.defMin !== '' || filters.defMax !== '' ? 1 : 0),
  )
</script>

<!-- Escape cascade (ui.escape): packpop -> zoom -> detail -> clear search. -->
<svelte:window
  onkeydown={(e) => {
    if (e.key === 'Escape') escape()
  }}
  ontouchstart={onTouchStart}
  ontouchend={onTouchEnd}
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
    <!-- Leaving Browse also drops the mobile drawers so they don't spring back
         open when the user returns. -->
    <button
      class:active={nav.view === 'deck'}
      onclick={() => {
        nav.view = 'deck'
        closeMobilePanels()
      }}>Deck</button
    >
    <button
      type="button"
      class="themebtn"
      onclick={toggleTheme}
      title={theme.mode === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
      aria-label={theme.mode === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
    >{theme.mode === 'dark' ? '☀' : '🌙'}</button>
  </nav>

  {#if nav.view === 'browse'}
    <SearchBar />
    {#if media.mobile}
      <div class="layout mobile">
        <CardTable />
      </div>
      <nav class="mbar">
        <button type="button" onclick={openMobileFilters}>
          Filters{#if fcount}<span class="bcnt">{fcount}</span>{/if}
        </button>
        <button type="button" onclick={openMobileDeck}>
          Deck<span class="bcnt">{counts.main}</span>
        </button>
      </nav>
      {#if layout.mFilters}
        <div class="scrim" transition:fade={{ duration: 140 }} use:clickSelf={closeMobilePanels}></div>
        <div class="drawer left" transition:fly={{ x: -340, duration: 200, opacity: 1 }}>
          <Filters sheet />
        </div>
      {/if}
      {#if layout.mDeck}
        <div class="scrim" transition:fade={{ duration: 140 }} use:clickSelf={closeMobilePanels}></div>
        <div class="drawer right" transition:fly={{ x: 340, duration: 200, opacity: 1 }}>
          <DeckPanel sheet />
        </div>
      {/if}
    {:else}
      <!-- Filters renders its own <aside>, CardTable its own <main>, so they drop
           straight into the .layout grid columns — the exact monolith DOM. -->
      <!-- Track widths follow the collapse store; a collapsed panel shrinks to a
           40px rail that still holds its expand button. -->
      <div
        class="layout"
        style="grid-template-columns:{layout.filters ? '250px' : '40px'} minmax(0,1fr) {layout.deck
          ? '290px'
          : '40px'}"
      >
        <Filters />
        <CardTable />
        <DeckPanel />
      </div>
    {/if}
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
  .viewbar .themebtn {
    margin-left: auto;
    padding: 5px 10px;
    font-size: 14px;
    line-height: 1;
  }
  @media (orientation: portrait) {
    .viewbar {
      padding: 6px 10px;
      gap: 5px;
    }
    .viewbar button {
      padding: 4px 14px;
      font-size: 12px;
    }
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
    color: var(--err);
  }

  /* Mobile bottom action bar (browse view). Bottom placement keeps both
     panel triggers in the thumb zone; safe-area padding clears the iOS
     home indicator. */
  .mbar {
    flex: 0 0 auto;
    display: flex;
    gap: 8px;
    padding: 8px 10px calc(8px + env(safe-area-inset-bottom));
    background: var(--panel);
    border-top: 1px solid var(--line);
  }
  .mbar button {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 7px;
    background: var(--panel2);
    border: 1px solid var(--line);
    color: var(--txt);
    padding: 11px;
    border-radius: 10px;
    cursor: pointer;
    font-size: 13.5px;
    font-family: inherit;
  }
  .bcnt {
    background: var(--accent2);
    color: #fff;
    border-radius: 9px;
    padding: 1px 8px;
    font-size: 11px;
    font-variant-numeric: tabular-nums;
  }

  /* Drawer overlays sit below the detail modal (z 20) so a card opened from
     the deck drawer stacks on top of it. */
  .scrim {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.45);
    z-index: 15;
  }
  .drawer {
    position: fixed;
    top: 0;
    bottom: 0;
    width: min(85vw, 340px);
    z-index: 16;
    background: var(--bg);
    display: flex;
    flex-direction: column;
  }
  .drawer.left {
    left: 0;
    box-shadow: 8px 0 30px rgba(0, 0, 0, 0.45);
  }
  .drawer.right {
    right: 0;
    box-shadow: -8px 0 30px rgba(0, 0, 0, 0.45);
  }
  .drawer > :global(aside) {
    flex: 1;
    min-height: 0;
    border-right: 0;
  }
  .drawer > :global(.deckpanel) {
    flex: 1;
    min-height: 0;
    border-left: 0;
  }
</style>

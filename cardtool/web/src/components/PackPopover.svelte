<script>
  // Fixed popover (monolith #packpop, packPopEnter 439-461, packPopLeave 462-464,
  // keep-alive 497-500). Driven entirely by ui.packpop = { idx, rect }: the anchor
  // pill (in CardDetail) sets it on hover; this component reads it, builds the
  // rarity-sorted pack contents and positions itself near the pill's rect.
  import { data } from '../lib/stores/data.svelte.js'
  import { ui, showDetail, cancelPackClose, schedulePackClose } from '../lib/stores/ui.svelte.js'
  import { media } from '../lib/stores/media.svelte.js'
  import { previewOn } from '../lib/stores/preview.svelte.js'
  import { RARITY_RANK, RARITY_BADGE } from '../lib/cards.js'
  import { activateKey, clickSelf } from '../lib/a11y.js'

  // Local pack box art is a public/ asset (packs/N.png) -> needs BASE_URL.
  const base = import.meta.env.VITE_DATA_BASE || import.meta.env.BASE_URL

  let popEl = $state()
  let x = $state(0)
  let y = $state(0)

  const card = $derived(ui.packpop ? data.byIdx.get(ui.packpop.idx) : null)
  const code = $derived(card?.pack ?? null)
  const meta = $derived(code ? data.packs[code] : null)
  // Pack contents sorted by rarity rank then name (monolith 443-444).
  const list = $derived.by(() => {
    if (!meta) return []
    return (data.packCards[code] || [])
      .slice()
      .sort((a, b) => RARITY_RANK[a.rarity] - RARITY_RANK[b.rarity] || a.name.localeCompare(b.name))
  })

  // Position near the anchor pill after render, flipping above when the popover
  // would overflow the viewport bottom (monolith 456-460). offsetHeight is read
  // after the DOM updates, so meta drives the reflow on pack change. Touch
  // devices skip this entirely: there the popover is a fixed bottom sheet —
  // an anchor-positioned floating panel over the detail content swallows
  // stray taps into pack rows.
  $effect(() => {
    if (!ui.packpop || !meta || !popEl || media.coarse) return
    const r = ui.packpop.rect
    // Lower clamp keeps the popover on-screen when the viewport is narrower
    // than its 320px width (innerWidth - 332 goes negative on small phones).
    x = Math.max(8, Math.min(r.left, innerWidth - 332))
    let ny = r.bottom + 8
    if (ny + popEl.offsetHeight > innerHeight - 8) ny = Math.max(8, r.top - 8 - popEl.offsetHeight)
    y = ny
  })

  // Keep-alive shares the single pack-close timer in ui.svelte.js with the anchor
  // pill (CardDetail), so hovering the popover cancels the close the pill armed on
  // leave; leaving the popover re-arms it (~180ms, monolith 462-464, 497-500).
</script>

{#if ui.packpop && meta}
  {#if media.coarse}
    <div class="pp-scrim" use:clickSelf={() => (ui.packpop = null)}></div>
  {/if}
  <!-- svelte-ignore a11y_no_static_element_interactions -->
  <div
    id="packpop"
    class:sheet={media.coarse}
    bind:this={popEl}
    style={media.coarse ? '' : `left:${x}px; top:${y}px;`}
    onmouseenter={cancelPackClose}
    onmouseleave={schedulePackClose}
  >
    <div class="pp-head">
      {#if meta.img}<img src={base + meta.img} alt="">{/if}
      <div>
        <div class="pp-title">{meta.full}</div>
        <div class="pp-sub">{code} · {list.length} card{list.length === 1 ? '' : 's'}</div>
      </div>
    </div>
    <div class="pp-list" use:previewOn>
      {#each list as c (c.idx)}
        {@const [ab, cls] = RARITY_BADGE[c.rarity] || ['', '']}
        <div
          class="pp-row"
          class:cur={c.idx === ui.packpop.idx}
          data-i={c.idx}
          role="button"
          tabindex="0"
          onclick={() => showDetail(data.byIdx.get(c.idx))}
          onkeydown={activateKey(() => showDetail(data.byIdx.get(c.idx)))}
        >
          <span class="rr {cls}">{ab}</span><span class="nm">{c.name}</span>
        </div>
      {/each}
    </div>
  </div>
{/if}

<style>
  /* Structural popover CSS (monolith 132-145). Rendered only when open, so the
     monolith's display:none + .show toggle collapses to display:flex here.
     The rarity chips and pixelated helper stay global in app.css. */
  #packpop {
    position: fixed;
    z-index: 45;
    width: 320px;
    max-width: calc(100vw - 16px);
    max-height: 70vh;
    display: flex;
    flex-direction: column;
    background: var(--panel);
    border: 1px solid var(--line);
    border-radius: 10px;
    box-shadow: 0 10px 34px rgba(0, 0, 0, 0.65);
    overflow: hidden;
  }
  .pp-head {
    display: flex;
    gap: 12px;
    padding: 12px;
    border-bottom: 1px solid var(--line);
  }
  .pp-head img {
    width: 72px;
    height: 144px;
    image-rendering: pixelated;
    border-radius: 5px;
    background: var(--panel2);
    flex-shrink: 0;
    object-fit: contain;
  }
  .pp-title {
    font-weight: 600;
    line-height: 1.3;
  }
  .pp-sub {
    color: var(--dim);
    font-size: 12px;
    margin-top: 4px;
  }
  .pp-list {
    overflow-y: auto;
    padding: 4px 0;
  }
  .pp-row {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 4px 12px;
    cursor: pointer;
    font-size: 12.5px;
  }
  .pp-row:hover {
    background: var(--panel2);
  }
  .pp-row.cur {
    background: rgba(240, 180, 41, 0.16);
  }
  .pp-row .nm {
    flex: 1;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .pp-scrim {
    position: fixed;
    inset: 0;
    z-index: 44;
    background: rgba(0, 0, 0, 0.45);
  }
  #packpop.sheet {
    left: 0;
    right: 0;
    bottom: 0;
    top: auto;
    width: auto;
    max-width: none;
    max-height: 70dvh;
    border-radius: 14px 14px 0 0;
    border-bottom: 0;
    padding-bottom: env(safe-area-inset-bottom);
  }
  #packpop.sheet .pp-row {
    padding: 10px 14px;
    font-size: 13.5px;
  }
</style>

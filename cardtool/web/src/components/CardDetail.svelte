<script>
  // Detail modal (monolith detail markup 171, showDetail 363-396, setArtTab
  // 420-431, backdrop close 501-503). Shown when ui.detailIdx != null.
  import { data } from '../lib/stores/data.svelte.js'
  import { ui, closeDetail, setArtTab, openZoom, cancelPackClose, schedulePackClose } from '../lib/stores/ui.svelte.js'
  import { media } from '../lib/stores/media.svelte.js'
  import { imgFull } from '../lib/cards.js'
  import LimitBadge from './LimitBadge.svelte'
  import CardFrame from './CardFrame.svelte'
  import { activateKey, clickSelf } from '../lib/a11y.js'
  import { add, canAdd, copiesOf, maxCopies, sectionOf } from '../lib/stores/deck.svelte.js'
  import { showToast } from '../lib/stores/toast.svelte.js'

  const card = $derived(ui.detailIdx == null ? null : data.byIdx.get(ui.detailIdx))

  // Meta line: monster shows attribute/race/kind, else cardType/icon.
  const line = $derived.by(() => {
    if (!card) return ''
    return card.cardType === 'Monster'
      ? [card.attribute, card.race, card.kind].filter(Boolean).join(' · ')
      : [card.cardType, card.icon].filter(Boolean).join(' · ')
  })

  // Pack pill hover -> pack popover (monolith packPopEnter/packPopLeave). The
  // 180ms close scheduled on leave is shared with PackPopover through ui.svelte.js,
  // so moving the cursor onto the popover cancels the pill's pending close.
  // On touch the enter path MUST stay dead: taps emit focus/mouseenter before
  // click, so an enter-opened popover mounts under the finger and the click
  // falls through onto a pack row — the pill toggles on click instead.
  function packEnter(e) {
    if (media.coarse) return
    cancelPackClose()
    ui.packpop = { idx: card.idx, rect: e.currentTarget.getBoundingClientRect() }
  }
  function packLeave() {
    schedulePackClose()
  }
  function packClick(e) {
    if (!media.coarse) return
    if (ui.packpop) {
      ui.packpop = null
      return
    }
    cancelPackClose()
    ui.packpop = { idx: card.idx, rect: e.currentTarget.getBoundingClientRect() }
  }

  const copies = $derived(card ? copiesOf(card) : 0)
  const cap = $derived(card ? maxCopies(card) : 3)
  const target = $derived(card ? sectionOf(card) : 'main')
  const canMain = $derived(card ? canAdd(card, target) : { ok: false })
  const canSide = $derived(card ? canAdd(card, 'side') : { ok: false })
  const addTo = (section) => {
    const r = add(card, section)
    if (!r.ok) showToast(r.reason)
  }
</script>

{#if card}
  <div id="detail" use:clickSelf={closeDetail}>
    <div class="card">
      <!-- Mobile-only: the modal goes full-screen there, so the close-by-backdrop
           affordance disappears and an explicit button is required. -->
      <button class="dclose" aria-label="Close" onclick={closeDetail}>×</button>
      <div class="dwrap">
        <div class="viewer">
          {#if imgFull(card)}
            <div class="tabs">
              <button class="tab" class:active={ui.artTab === 'card'} onclick={() => setArtTab('card')}>Card</button>
              <button class="tab" class:active={ui.artTab === 'art'} onclick={() => setArtTab('art')}>Game art</button>
            </div>
          {/if}
          {#if ui.artTab === 'card' && imgFull(card)}
            <!-- svelte-ignore a11y_no_noninteractive_element_to_interactive_role -->
            <img class="cardimg" src={imgFull(card)} alt="" role="button" tabindex="0" aria-label="Zoom card image" onclick={() => openZoom(imgFull(card), 0)} onkeydown={activateKey(() => openZoom(imgFull(card), 0))} onerror={() => setArtTab('art')}>
          {:else if card.art}
            <CardFrame {card} />
          {/if}
        </div>
        <div class="dtext">
          <h2>{card.name}</h2>
          <div class="meta"><span class="badge t-{card.cardType}">{card.cardType}</span> &nbsp; {line}</div>
          <div class="deckadd">
            <button type="button" class="addbtn" disabled={!canMain.ok} title={canMain.ok ? '' : canMain.reason} onclick={() => addTo(target)}>+ {target === 'extra' ? 'Extra' : 'Main'} Deck</button>
            <button type="button" class="addbtn alt" disabled={!canSide.ok} title={canSide.ok ? '' : canSide.reason} onclick={() => addTo('side')}>+ Side</button>
            <span class="incount">In deck: {copies} / {cap}</span>
          </div>
          {#if card.cardType === 'Monster'}
            <div class="stats">
              <div><span>Level</span><b>{card.level ?? '—'}</b></div>
              <div><span>ATK</span><b>{card.atk ?? '—'}</b></div>
              <div><span>DEF</span><b>{card.def ?? '—'}</b></div>
            </div>
          {/if}
          <div class="effect">{card.effect || ''}</div>
          <div class="dmeta">
            {#if card.limit}
              <span class="pill"><b>Limit</b><LimitBadge limit={card.limit} size={16} /> {card.limit}</span>
            {/if}
            {#if card.pack}
              <span class="pill packpill" role="button" tabindex="0" onmouseenter={packEnter} onmouseleave={packLeave} onfocus={packEnter} onblur={packLeave} onclick={packClick} onkeydown={activateKey(packClick)}><b>Pack</b>{card.pack}</span>
            {/if}
            {#if card.rarity}
              <span class="pill"><b>Rarity</b>{card.rarity}</span>
            {/if}
            {#if card.password}
              <span class="pill"><b>Password</b>{String(card.password).padStart(8, '0')}</span>
            {/if}
            <span class="pill"><b>ID</b>{card.id}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
{/if}

<style>
  /* Structural detail-modal CSS (monolith 82-96, 113-126, 131, 150). Shared and
     interpolated classes (pix, badge, t-, ycard, yc-) stay global in app.css. */
  #detail { position:fixed; inset:0; background:rgba(0,0,0,.55); display:flex;
    align-items:center; justify-content:center; z-index:20; }
  .card { position:relative; background:var(--panel); border:1px solid var(--line); border-radius:12px;
    max-width:840px; width:94%; max-height:90vh; overflow-y:auto; padding:24px; }
  .dclose { display:none; }
  .dwrap { display:flex; gap:22px; align-items:flex-start; }
  .cardimg { width:260px; border-radius:9px; flex-shrink:0; background:var(--panel2); cursor:zoom-in; }
  .viewer { flex-shrink:0; }
  .tabs { display:flex; gap:4px; margin-bottom:8px; }
  .tab { background:var(--panel2); border:1px solid var(--line); color:var(--dim);
    padding:4px 12px; border-radius:7px; cursor:pointer; font-size:12px; font-family:inherit; }
  .tab:hover { color:var(--accent); }
  .tab.active { background:var(--accent2); border-color:var(--accent2); color:#fff; }
  .dtext { flex:1; min-width:0; }
  .card h2 { margin:0 0 4px; }
  .card .meta { color:var(--dim); margin-bottom:14px; }
  .deckadd { display:flex; align-items:center; gap:8px; flex-wrap:wrap; margin-bottom:14px; }
  .addbtn { background:var(--accent2); border:1px solid var(--accent2); color:#fff;
    padding:6px 12px; border-radius:8px; cursor:pointer; font-size:12.5px; font-family:inherit; }
  .addbtn.alt { background:var(--panel2); border-color:var(--line); color:var(--txt); }
  .addbtn:hover:not(:disabled) { filter:brightness(1.1); }
  .addbtn:disabled { opacity:.45; cursor:not-allowed; }
  .incount { color:var(--dim); font-size:12px; font-variant-numeric:tabular-nums; }
  .card .stats { display:flex; gap:18px; flex-wrap:wrap; margin:12px 0; padding:12px 0;
    border-top:1px solid var(--line); border-bottom:1px solid var(--line); }
  .card .stats div span { display:block; font-size:11px; color:var(--dim);
    text-transform:uppercase; letter-spacing:.05em; }
  .card .stats div b { font-size:16px; }
  .card .effect { white-space:pre-wrap; line-height:1.55; }
  .dmeta { display:flex; flex-wrap:wrap; gap:8px; margin-top:18px;
    border-top:1px solid var(--line); padding-top:16px; }
  .pill { background:var(--panel2); border:1px solid var(--line); border-radius:8px;
    padding:4px 10px; font-size:12px; color:var(--dim); }
  .pill b { color:var(--txt); font-weight:600; margin-right:6px; }
  .packpill { cursor:help; }
  @media (orientation:portrait) {
    #detail { align-items:stretch; }
    .card { width:100%; max-width:none; max-height:none; border-radius:0; border:0;
      padding:16px 14px calc(16px + env(safe-area-inset-bottom)); }
    .dclose { display:grid; place-items:center; position:absolute; top:10px; right:10px;
      width:36px; height:36px; border-radius:50%; background:var(--panel2);
      border:1px solid var(--line); color:var(--txt); font-size:20px; cursor:pointer; z-index:1; }
    .dwrap { flex-direction:column; }
    .viewer { align-self:center; }
    .cardimg { width:min(240px, 60vw); }
    .card h2 { padding-right:40px; }
    .addbtn { padding:10px 14px; }
  }
</style>

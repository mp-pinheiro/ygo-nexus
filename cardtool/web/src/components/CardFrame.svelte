<script>
  // Faux in-game card frame (monolith cardFrame(), index.legacy.html 405-418).
  // All visual classes (.ycard/.f-*/.yc-*/.pix) are global in app.css.
  import { FRAME } from '../lib/cards.js'
  import { openZoom } from '../lib/stores/ui.svelte.js'

  const base = import.meta.env.BASE_URL

  let { card } = $props()

  const mon = $derived(card.cardType === 'Monster')
  const badge = $derived(mon ? card.attribute : card.icon)
  const stars = $derived('★'.repeat(Math.min(card.level, 12)) || '·')
  const typeline = $derived(
    mon
      ? `[ ${[card.race, ...(card.types || [])].filter(Boolean).join(' / ')} ]`
      : `[ ${[card.cardType, card.icon].filter(Boolean).join(' / ')} ]`,
  )
</script>

<div class="ycard f-{FRAME(card)}">
  <div class="yc-name"><span>{card.name}</span>{#if badge}<span class="yc-attr">{badge}</span>{/if}</div>
  <div class="yc-art"><img class="pix" src={base + card.art} alt="" onclick={() => openZoom(base + card.art, 1)}></div>
  {#if mon && card.level != null}<div class="yc-lvl">{stars}<b> Lv {card.level}</b></div>{/if}
  <div class="yc-type">{typeline}</div>
  <div class="yc-text">{card.effect || ''}</div>
  {#if mon}<div class="yc-stats">ATK / {card.atk ?? '?'}　DEF / {card.def ?? '?'}</div>{/if}
</div>

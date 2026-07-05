<script>
  // SVG badge so the slash and the 1/2 stay centred on every OS/font. CSS
  // flex-centring positions the glyph by per-font side-bearings and baseline,
  // so a text badge that looks centred in one font is lopsided in another
  // (e.g. Linux system-ui vs Windows Segoe UI). SVG places geometry, not glyphs.
  import { LIMIT_STYLE } from '../lib/cards.js'

  let { limit, size = 20 } = $props()

  const s = $derived(limit ? LIMIT_STYLE[limit] : null)
</script>

{#if s}
  <svg class="lmb" viewBox="0 0 20 20" width={size} height={size} role="img" aria-label={limit}>
    <title>{limit}</title>
    <circle cx="10" cy="10" r="9.25" fill={s.fill} stroke="rgba(0,0,0,0.3)" stroke-width="0.75" />
    {#if s.slash}
      <line x1="6.3" y1="6.3" x2="13.7" y2="13.7" stroke="#fff" stroke-width="2.4" stroke-linecap="round" />
    {:else}
      <text x="10" y="10" text-anchor="middle" dominant-baseline="central" fill={s.color}
        font-size="12.5" font-weight="700" style="font-variant-numeric:tabular-nums">{s.text}</text>
    {/if}
  </svg>
{/if}

<style>
  .lmb { display:inline-block; vertical-align:middle; }
</style>

<script>
  // Renders the store-driven floating thumbnail (monolith #img preview, 170).
  // All mousemove/position logic lives in the previewOn action; this component
  // only reflects preview.{url,x,y,visible} onto a fixed <img>. imgSmall URLs
  // are absolute YGOPRODeck links, so no BASE_URL prefix. onerror caches the
  // 404 via markBad so the broken image never retries or flashes.
  import { preview, markBad } from '../lib/stores/preview.svelte.js'
</script>

<img
  id="preview"
  alt=""
  src={preview.url}
  style="left:{preview.x}px; top:{preview.y}px; display:{preview.visible ? 'block' : 'none'};"
  onerror={() => markBad(preview.url)}
/>

<style>
  #preview {
    position: fixed;
    width: 176px;
    border-radius: 9px;
    display: none;
    z-index: 60;
    pointer-events: none;
    border: 1px solid var(--line);
    background: var(--panel2);
    box-shadow: 0 6px 26px rgba(0, 0, 0, 0.7);
  }
</style>

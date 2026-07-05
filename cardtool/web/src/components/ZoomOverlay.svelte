<script>
  import { ui } from '../lib/stores/ui.svelte.js'
</script>

{#if ui.zoom}
  <div id="zoom" onclick={() => (ui.zoom = null)}>
    <img class:pix={ui.zoom.pix} src={ui.zoom.url} alt="">
  </div>
{/if}

<style>
  #zoom {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, .85);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 50;
    cursor: zoom-out;
  }
  #zoom img {
    max-width: 92vw;
    max-height: 92vh;
    border-radius: 10px;
    box-shadow: 0 8px 40px rgba(0, 0, 0, .8);
  }
</style>

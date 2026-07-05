<script>
  import { toast } from '../lib/stores/toast.svelte.js'
</script>

{#if toast.msg}
  <div class="toast" role="status" aria-live="polite">{toast.msg}</div>
{/if}

<style>
  .toast {
    position: fixed;
    bottom: 22px;
    left: 50%;
    transform: translateX(-50%);
    background: var(--panel2);
    border: 1px solid var(--line);
    color: var(--txt);
    padding: 9px 16px;
    border-radius: 8px;
    box-shadow: 0 6px 22px rgba(0, 0, 0, 0.6);
    font-size: 13px;
    z-index: 80;
    pointer-events: none;
  }
</style>

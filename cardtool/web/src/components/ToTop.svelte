<script>
  import { fade } from 'svelte/transition'

  let wrap = $state(null)
  let visible = $state(false)

  $effect(() => {
    const el = wrap?.parentElement
    if (!el) return
    const onScroll = () => (visible = el.scrollTop > 300)
    onScroll()
    el.addEventListener('scroll', onScroll, { passive: true })
    return () => el.removeEventListener('scroll', onScroll)
  })
</script>

<div class="wrap" bind:this={wrap}>
  {#if visible}
    <button
      type="button"
      transition:fade={{ duration: 140 }}
      onclick={() => wrap.parentElement.scrollTo({ top: 0, behavior: 'smooth' })}
      aria-label="Scroll to top"
      title="Scroll to top">↑</button
    >
  {/if}
</div>

<style>
  .wrap {
    position: sticky;
    bottom: 14px;
    height: 0;
    display: flex;
    justify-content: flex-end;
    padding-right: 14px;
    z-index: 5;
    pointer-events: none;
  }
  button {
    pointer-events: auto;
    transform: translateY(-100%);
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: var(--panel2);
    border: 1px solid var(--line);
    color: var(--txt);
    font-size: 17px;
    line-height: 1;
    cursor: pointer;
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.35);
  }
  button:hover {
    border-color: var(--accent2);
    color: var(--accent2);
  }
</style>

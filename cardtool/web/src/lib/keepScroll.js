// Action: remember a scroll container's position across unmounts. The
// Browse|Deck view toggle destroys each view's DOM, so scrollTop is captured
// on every scroll (reading it in destroy is unreliable — the node may already
// be detached) and restored on the next mount. Keyed so containers coexist.
const positions = new Map()

export function keepScroll(node, key) {
  node.scrollTop = positions.get(key) ?? 0
  const save = () => positions.set(key, node.scrollTop)
  node.addEventListener('scroll', save, { passive: true })
  return {
    destroy() {
      node.removeEventListener('scroll', save)
    },
  }
}

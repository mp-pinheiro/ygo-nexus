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

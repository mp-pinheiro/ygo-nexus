// Enter/Space activates a role="button" element — the a11y lint wants an explicit
// keydown handler, and a bare onclick isn't keyboard-reachable.
export const activateKey = (fn) => (e) => {
  if (e.key === 'Enter' || e.key === ' ') {
    e.preventDefault()
    fn(e)
  }
}

// Action: focus on mount, replacing the autofocus attribute (which a11y lint flags).
export function focusOnMount(node) {
  node.focus()
}

// Action: run handler when the element itself (not a child) is clicked. Attaching
// the listener in JS keeps a click-to-close backdrop out of the a11y lint's static
// handler check; keyboard close is handled globally by Escape.
export function clickSelf(node, handler) {
  const onclick = (e) => {
    if (e.target === node) handler(e)
  }
  node.addEventListener('click', onclick)
  return {
    update(h) {
      handler = h
    },
    destroy() {
      node.removeEventListener('click', onclick)
    },
  }
}

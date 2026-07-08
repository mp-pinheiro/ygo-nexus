// Top-level view toggle: 'browse' | 'deck'.
export const nav = $state({ view: 'browse' })

// In-app navigation stack so the browser back button/gesture navigates
// within the app instead of leaving the page.
const stack = []
let ignoreNext = false

export function navPush(tag) {
  stack.push(tag)
  history.pushState({ app: tag }, '')
}

export function navPop() {
  if (stack.length) {
    ignoreNext = true
    history.back()
    return stack.pop()
  }
  return null
}

export function navClear() {
  while (stack.length) {
    ignoreNext = true
    history.back()
    stack.pop()
  }
}

export function initPopState(onBack) {
  window.addEventListener('popstate', (e) => {
    if (ignoreNext) { ignoreNext = false; return }
    const tag = stack.pop()
    if (tag) onBack(tag)
    else history.pushState(null, '')
  })
  history.replaceState(null, '')
}

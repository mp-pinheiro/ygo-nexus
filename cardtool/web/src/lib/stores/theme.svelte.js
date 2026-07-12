// Light/dark theme toggle. index.html sets data-theme on <html> before first
// paint (no flash); this store re-reads the same key, keeps the attribute in
// sync, and persists explicit choices. No stored value = follow the OS.
const KEY = 'nexus.theme'

function stored() {
  try {
    const v = localStorage.getItem(KEY)
    return v === 'light' || v === 'dark' ? v : null
  } catch {
    return null
  }
}

function systemTheme() {
  return matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark'
}

export const theme = $state({ mode: stored() ?? systemTheme() })

function apply() {
  document.documentElement.dataset.theme = theme.mode
}
apply()

export function toggleTheme() {
  theme.mode = theme.mode === 'light' ? 'dark' : 'light'
  apply()
  try {
    localStorage.setItem(KEY, theme.mode)
  } catch {
    // Private mode / storage disabled — the toggle still works for the session.
  }
}

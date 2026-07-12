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
  } catch {}
}

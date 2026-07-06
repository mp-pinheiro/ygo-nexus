// Reactive viewport/input-mode flags. The mobile/desktop split is by
// ORIENTATION, not width — a portrait iPad (1024x1366) is unusable with the
// desktop 3-column grid, while any landscape viewport fits it. Must match the
// @media (orientation: portrait) blocks across app.css and the components —
// CSS media queries cannot read JS constants, so the rule is duplicated by
// convention.
const portrait = matchMedia('(orientation: portrait)')
const hoverless = matchMedia('(hover: none)')

export const media = $state({ mobile: portrait.matches, coarse: hoverless.matches })

portrait.addEventListener('change', (e) => {
  media.mobile = e.matches
})
hoverless.addEventListener('change', (e) => {
  media.coarse = e.matches
})

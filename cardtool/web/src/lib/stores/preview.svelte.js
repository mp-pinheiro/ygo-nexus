// Shared mouse-follow hover-preview infra (monolith 473-493). The previewOn
// action attaches to a scroll container (table tbody, pack list); on mousemove
// it resolves the hovered [data-i] row to a card and positions an external
// thumbnail. badImg caches 404s so a broken image never retries or flashes.
import { data } from './data.svelte.js'
import { imgSmall } from '../cards.js'

export const preview = $state({ url: null, x: 0, y: 0, visible: false })

// Touch browsers fire synthetic mousemove on tap, which would flash the
// thumbnail at the tap point; hover previews only make sense with a pointer.
const noHover = matchMedia('(hover: none)')

const badImg = new Set()

export function markBad(url) {
  badImg.add(url)
  preview.visible = false
}

export function previewOn(node) {
  const onMove = (e) => {
    if (noHover.matches) return
    const el = e.target.closest('[data-i]')
    const card = el && data.byIdx.get(+el.dataset.i)
    const url = card && imgSmall(card)
    if (!url || badImg.has(url)) {
      preview.visible = false
      return
    }
    preview.url = url
    const w = 176
    const h = 254
    let x = e.clientX + 20
    if (x + w > innerWidth) x = e.clientX - w - 20
    const y = Math.max(8, Math.min(e.clientY - h / 2, innerHeight - h - 8))
    preview.x = x
    preview.y = y
    preview.visible = true
  }
  const onLeave = () => {
    preview.visible = false
  }
  node.addEventListener('mousemove', onMove)
  node.addEventListener('mouseleave', onLeave)
  return {
    destroy() {
      node.removeEventListener('mousemove', onMove)
      node.removeEventListener('mouseleave', onLeave)
    },
  }
}

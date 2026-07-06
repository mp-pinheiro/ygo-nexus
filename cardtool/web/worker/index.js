// Cloudflare Worker: serves the built SPA (ASSETS), the card data from R2
// (/data/*), and the KV-backed deck API (/api/decks). Cloudflare Access gates
// the whole hostname, so the R2 data + decks are never public.

const JSON_CT = { 'content-type': 'application/json; charset=utf-8' }

// Access injects the authenticated user's email; decks are keyed by it so they
// sync per-user. Falls back to a shared key when run outside Access (local dev).
const deckKey = (request) => `decks:${request.headers.get('Cf-Access-Authenticated-User-Email') || 'local'}`

async function handleDecks(request, env) {
  const key = deckKey(request)
  if (request.method === 'GET') {
    const body = await env.DECKS.get(key)
    return new Response(body ?? 'null', { headers: JSON_CT })
  }
  if (request.method === 'PUT') {
    await env.DECKS.put(key, await request.text())
    return new Response('{"ok":true}', { headers: JSON_CT })
  }
  return new Response('Method Not Allowed', { status: 405 })
}

async function handleData(env, url) {
  const objKey = decodeURIComponent(url.pathname.replace(/^\/data\//, ''))
  const obj = await env.DATA.get(objKey)
  if (!obj) return new Response('Not found', { status: 404 })
  const headers = new Headers()
  obj.writeHttpMetadata(headers)
  headers.set('etag', obj.httpEtag)
  headers.set('cache-control', 'public, max-age=86400')
  if (objKey.endsWith('.json')) headers.set('content-type', JSON_CT['content-type'])
  else if (objKey.endsWith('.png')) headers.set('content-type', 'image/png')
  return new Response(obj.body, { headers })
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url)
    if (url.pathname === '/api/decks') return handleDecks(request, env)
    if (url.pathname.startsWith('/data/')) return handleData(env, url)
    return env.ASSETS.fetch(request)
  },
}

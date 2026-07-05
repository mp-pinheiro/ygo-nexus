#!/usr/bin/env python3
"""Static dev server for the card app, with live reload.

Serves this directory and injects a small poller into HTML responses so the
browser refreshes whenever a file here changes -- edit index.html, or re-run
`python cardtool/extract.py` to regenerate cards.js, and the page reloads itself.

    python cardtool/web/serve.py [port=8000]
"""
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

WEB = Path(__file__).resolve().parent
POLL = b"""
<script>
(() => {
  let seen = null;
  setInterval(async () => {
    try {
      const t = await (await fetch('/__reload', { cache: 'no-store' })).text();
      if (seen === null) seen = t; else if (t !== seen) location.reload();
    } catch (e) {}
  }, 600);
})();
</script>"""


def watch_token():
    stamps = [p.stat().st_mtime for p in WEB.iterdir()
              if p.is_file() and p.suffix in ('.html', '.js', '.css')]
    return repr(max(stamps, default=0.0))


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=str(WEB), **k)

    def do_GET(self):
        path = self.path.split('?')[0]
        if path == '/__reload':
            return self._send(watch_token().encode(), 'text/plain')
        if path == '/' or path.endswith('.html'):
            fp = WEB / ('index.html' if path == '/' else path.lstrip('/'))
            if fp.is_file():
                html = fp.read_bytes()
                html = html.replace(b'</body>', POLL + b'</body>') if b'</body>' in html else html + POLL
                return self._send(html, 'text/html; charset=utf-8')
        return super().do_GET()

    def _send(self, body, ctype):
        self.send_response(200)
        self.send_header('Content-Type', ctype)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        if not self.path.startswith('/__reload'):
            super().log_message(fmt, *args)


if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    print(f"Card search (live reload)  ->  http://localhost:{port}")
    ThreadingHTTPServer(('', port), Handler).serve_forever()

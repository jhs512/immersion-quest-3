"""Small observable server: identity, peer address and destination address."""
import http.server
import json
import os
from pathlib import Path


class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        body = json.dumps({"server": os.environ["LAB_ROLE"],
                           "peer": self.client_address[0],
                           "local": self.connection.getsockname()[0]}).encode()
        self.send_response(200)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *_):
        pass


bind = Path("/config/bind.txt").read_text().strip()
http.server.ThreadingHTTPServer((bind, 8080), Handler).serve_forever()

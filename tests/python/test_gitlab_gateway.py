import json
import threading
import time
import unittest
from pathlib import Path
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import requests
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'assets/gitlab'))
import lab


class GatewayTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        class Upstream(BaseHTTPRequestHandler):
            def log_message(self, *_args):
                pass

            def do_GET(self):
                if self.path == '/users/sign_in':
                    content = b'<meta name="csrf-token" content="test-csrf">'
                else:
                    content = json.dumps({'cookie': self.headers.get('Cookie'),
                                          'authorization': self.headers.get('Authorization'),
                                          'token': self.headers.get('PRIVATE-TOKEN')}).encode()
                self.send_response(200)
                self.send_header('Content-Length', str(len(content)))
                self.send_header('Set-Cookie', 'private_session=server-only; Path=/; HttpOnly')
                self.end_headers()
                self.wfile.write(content)

            def do_POST(self):
                self.rfile.read(int(self.headers.get('Content-Length', 0)))
                self.send_response(302)
                self.send_header('Set-Cookie', 'private_session=server-only; Path=/; HttpOnly')
                self.send_header('Location', '/')
                self.send_header('Content-Length', '0')
                self.end_headers()

        cls.upstream = ThreadingHTTPServer(('127.0.0.1', 0), Upstream)
        threading.Thread(target=cls.upstream.serve_forever, daemon=True).start()
        cls.port = lab.free_port()
        cls.url = f'http://127.0.0.1:{cls.port}'
        config = dict(port=cls.port, internal_port=cls.upstream.server_port, url=cls.url,
                      username='mq_learner', password='test-only-password', api_token='test-only-token')
        lab.load = lambda: config
        threading.Thread(target=lab.serve, daemon=True).start()
        for _ in range(50):
            try:
                if requests.get(cls.url + '/__mq/health', timeout=1).ok:
                    break
            except requests.RequestException:
                time.sleep(.02)

    @classmethod
    def tearDownClass(cls):
        cls.upstream.shutdown()

    def test_web_session_is_automatic_and_never_given_to_browser(self):
        response = requests.get(self.url + '/mq_learner/project', timeout=5)
        self.assertEqual(response.status_code, 200)
        self.assertIn('private_session=server-only', response.json()['cookie'])
        self.assertNotIn('Set-Cookie', response.headers)

    def test_api_uses_only_dedicated_token(self):
        response = requests.get(self.url + '/api/v4/user',
                                headers={'PRIVATE-TOKEN': 'untrusted', 'Cookie': 'attacker=1'}, timeout=5)
        self.assertEqual(response.json()['token'], 'test-only-token')
        self.assertNotIn('attacker', response.json()['cookie'])

    def test_git_gets_http_credentials_without_a_prompt(self):
        response = requests.get(self.url + '/mq_learner/demo.git/info/refs?service=git-upload-pack', timeout=5)
        self.assertTrue(response.json()['authorization'].startswith('Basic '))

    def test_foreign_browser_cannot_make_requests_or_rebind_host(self):
        response = requests.post(self.url + '/api/v4/projects',
                                 headers={'Origin': 'https://example.com'}, timeout=5)
        self.assertEqual(response.status_code, 403)
        response = requests.get(self.url + '/', headers={'Host': 'attacker.invalid'}, timeout=5)
        self.assertEqual(response.status_code, 403)


if __name__ == '__main__':
    unittest.main()

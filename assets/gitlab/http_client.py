"""Small stdlib HTTP adapter; the bundled lab requires no pip packages."""
import http.cookiejar
import json as _json
import urllib.error
import urllib.request


class RequestException(RuntimeError):
    pass


class Response:
    def __init__(self, result):
        self.status_code = result.code
        self.headers = result.headers
        self.url = result.url
        self.content = result.read()
        result.close()
        self.text = self.content.decode('utf-8', errors='replace')
        self.ok = 200 <= self.status_code < 400

    def json(self):
        return _json.loads(self.content)

    def raise_for_status(self):
        if not self.ok:
            raise RequestException('HTTP ' + str(self.status_code))


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *_args, **_kwargs):
        return None


class Session:
    def __init__(self):
        self.headers = {}
        self.cookies = http.cookiejar.CookieJar()

    def request(self, method, url, *, headers=None, data=None, json=None,
                params=None, timeout=60, allow_redirects=True):
        from urllib.parse import urlencode
        all_headers = {**self.headers, **(headers or {})}
        if params:
            url += ('&' if '?' in url else '?') + urlencode(params)
        if json is not None:
            data = _json.dumps(json).encode()
            all_headers['Content-Type'] = 'application/json'
        elif isinstance(data, dict):
            data = urlencode(data).encode()
            all_headers['Content-Type'] = 'application/x-www-form-urlencoded'
        handlers = [urllib.request.ProxyHandler({}), urllib.request.HTTPCookieProcessor(self.cookies)]
        if not allow_redirects:
            handlers.append(NoRedirect())
        request = urllib.request.Request(url, data=data, headers=all_headers, method=method)
        try:
            return Response(urllib.request.build_opener(*handlers).open(request, timeout=timeout))
        except urllib.error.HTTPError as response:
            return Response(response)
        except (OSError, urllib.error.URLError) as error:
            raise RequestException(str(error)) from error

    def get(self, url, **kwargs):
        return self.request('GET', url, **kwargs)

    def post(self, url, **kwargs):
        return self.request('POST', url, **kwargs)


class requests:
    Session = Session
    RequestException = RequestException

    @staticmethod
    def request(method, url, **kwargs):
        return Session().request(method, url, **kwargs)

    @staticmethod
    def get(url, **kwargs):
        return requests.request('GET', url, **kwargs)

    @staticmethod
    def post(url, **kwargs):
        return requests.request('POST', url, **kwargs)

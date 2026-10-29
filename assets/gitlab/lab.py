"""Loopback-only GitLab lab. A dedicated ordinary account is automatic, not root.

The gateway owns the account's web session, Git HTTP credentials and API token.
They never need to be entered by the learner. This is a shared local exercise
identity, not an anonymous production GitLab authentication configuration.
"""
import argparse
import base64
import html.parser
import json
import os
from pathlib import Path
import secrets
import socket
import subprocess
import sys
import threading
import time
import shutil
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit

from http_client import requests

ROOT = Path(__file__).resolve().parent
STATE = Path(os.environ.get('MQ3_GITLAB_STATE', ROOT / '.state')).resolve()
CONFIG = STATE / 'config.json'

# Finder and an app launched before Docker installation can inherit a minimal PATH.
if not shutil.which('docker'):
    candidates=[Path(os.environ.get('ProgramFiles','C:/Program Files'))/'Docker/Docker/resources/bin',
                Path('/Applications/Docker.app/Contents/Resources/bin'),Path('/usr/local/bin')]
    for directory in candidates:
        if (directory/('docker.exe' if os.name=='nt' else 'docker')).is_file():
            os.environ['PATH']=str(directory)+os.pathsep+os.environ.get('PATH','')
            break


def ensure_docker():
    def ready():
        try:
            return subprocess.run(['docker','info','--format','{{.OSType}}'],capture_output=True,timeout=8).returncode==0
        except (OSError,subprocess.TimeoutExpired):
            return False
    if ready():return
    if os.name=='nt':
        desktop=Path(os.environ.get('ProgramFiles','C:/Program Files'))/'Docker/Docker/Docker Desktop.exe'
        if desktop.is_file():subprocess.Popen([str(desktop)],creationflags=subprocess.CREATE_NO_WINDOW)
    elif sys.platform=='darwin':
        subprocess.Popen(['open','-g','-a','Docker'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    for _ in range(60):
        if ready():return
        time.sleep(2)
    raise RuntimeError('Docker Desktop did not become ready. Install or start Docker Desktop.')


def save(config):
    CONFIG.write_text(json.dumps(config, indent=2), encoding='utf-8')


def load():
    return json.loads(CONFIG.read_text(encoding='utf-8'))


def command(*args, **kwargs):
    result = subprocess.run(args, capture_output=True, text=True,
                            encoding='utf-8', errors='replace', **kwargs)
    if result.returncode:
        raise RuntimeError(f'{args[0]} failed: {result.stderr[:1000]}')
    return result.stdout.strip()


def free_port():
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
        return sock.getsockname()[1]


def api(config, method, path, **kwargs):
    response = requests.request(method, config['url'] + '/api/v4' + path,
                                timeout=60, **kwargs)
    if not response.ok:
        raise RuntimeError(f'GitLab API {method} {path}: {response.status_code}')
    return response.json() if response.content else None


def owned(name, role):
    """Return the container's metadata only if this lab created it; None when absent."""
    found = subprocess.run(['docker', 'inspect', '--type', 'container', name], capture_output=True,
                           text=True, encoding='utf-8', errors='replace')
    if found.returncode:
        return None
    metadata = json.loads(found.stdout)[0]
    if (metadata['Config'].get('Labels') or {}).get('mq3.role') != role:
        raise RuntimeError('Refusing to manage a container not owned by this lab: ' + name)
    return metadata


def gateway_healthy(config):
    """True only when this lab's gateway (not another program on the port) answers."""
    try:
        response = requests.get(config['url'] + '/__mq/health', timeout=2)
        data = response.json() if response.ok else {}
    except (requests.RequestException, ValueError):
        return False
    return data.get('identity') == config['username'] and data.get('local_only') is True


def start():
    ensure_docker()
    STATE.mkdir(parents=True,exist_ok=True)
    if CONFIG.exists():
        config = load()
    else:
        web, internal = free_port(), free_port()
        while web == internal:
            internal = free_port()
        config = dict(name='mq3-gitlab-' + secrets.token_hex(4), port=web,
                      internal_port=internal, url=f'http://127.0.0.1:{web}',
                      username='mq_learner', password=secrets.token_urlsafe(30))
        (STATE / 'root-password').write_text(secrets.token_urlsafe(36), encoding='utf-8')
        save(config)
    if owned(config['name'], 'local-gitlab-lab') is None:
        image = 'gitlab/gitlab-ce:19.5.1-ce.0'
        inspected = subprocess.run(['docker','image','inspect',image],capture_output=True)
        if inspected.returncode:
            print('Downloading the official GitLab image.', flush=True)
            command('docker','pull','--platform','linux/amd64',image,timeout=1800)
        digest = json.loads(command('docker', 'image', 'inspect', image))[0]['RepoDigests'][0]
        config['image'] = digest
        save(config)
        settings = f"""external_url '{config['url']}';
nginx['listen_port'] = 80;
letsencrypt['enable'] = false;
gitlab_rails['initial_root_password'] = File.read('/run/secrets/mq-root-password').strip;
gitlab_rails['smtp_enable'] = false;
gitlab_rails['gitlab_default_projects_features_builds'] = false;
puma['worker_processes'] = 0;
puma['min_threads'] = 1;
puma['max_threads'] = 4;
sidekiq['concurrency'] = 5;
prometheus_monitoring['enable'] = false;
registry['enable'] = false;
gitlab_pages['enable'] = false;
"""
        command('docker', 'run', '-d', '--platform','linux/amd64','--name', config['name'],
                '--label', 'mq3.role=local-gitlab-lab', '--restart', 'no',
                '--memory', '8g', '--cpus', '4', '--shm-size', '256m',
                '-p', f"127.0.0.1:{config['internal_port']}:80",
                '--mount', f"type=bind,src={STATE / 'root-password'},dst=/run/secrets/mq-root-password,readonly",
                '-v', config['name'] + '-config:/etc/gitlab',
                '-v', config['name'] + '-logs:/var/log/gitlab',
                '-v', config['name'] + '-data:/var/opt/gitlab',
                '-e', 'GITLAB_OMNIBUS_CONFIG=' + settings, digest, timeout=60)
    else:
        command('docker', 'start', config['name'], timeout=60)
    print('Starting local GitLab container ' + config['name'], flush=True)
    deadline = time.monotonic() + 1200
    next_report = 0
    while time.monotonic() < deadline:
        try:
            # Docker NAT may not belong to GitLab's monitoring allowlist.
            # A fully rendered Rails sign-in form proves the web app is ready.
            ready = requests.get(f"http://127.0.0.1:{config['internal_port']}/users/sign_in", timeout=5)
            if ready.status_code == 200 and 'csrf-token' in ready.text:
                break
        except requests.RequestException:
            pass
        if time.monotonic() >= next_report:
            print('GitLab initialization in progress.', flush=True)
            next_report = time.monotonic() + 30
        time.sleep(5)
    else:
        raise RuntimeError('GitLab readiness timeout; inspect this lab container only.')
    token_valid = False
    if config.get('api_token'):
        probe = requests.get(f"http://127.0.0.1:{config['internal_port']}/api/v4/user",
                             headers={'PRIVATE-TOKEN': config['api_token']}, timeout=30)
        token_valid = probe.status_code == 200
    if not token_valid:
        payload = json.dumps(dict(username=config['username'], password=config['password']))
        ruby = """require 'json'
c = JSON.parse(STDIN.read)
root = User.find_by_username!('root')
u = User.find_by_username(c['username'])
unless u
  params = { username: c['username'], name: 'MQ learner', email: 'mq-learner@example.invalid',
             password: c['password'], password_confirmation: c['password'], skip_confirmation: true,
             organization_id: Organizations::Organization.default_organization.id }
  response = Users::CreateService.new(root, params).execute
  raise response.message if response.error?
  u = response.payload[:user]
  raise u.errors.full_messages.join('; ') unless u.persisted?
end
u.confirm unless u.confirmed?
t = u.personal_access_tokens.create!(name: 'MQ local lab', scopes: ['api','write_repository'], expires_at: 30.days.from_now.to_date)
ApplicationSetting.current.update!(signup_enabled: false)
puts JSON.generate({token: t.token, id: u.id, admin: u.admin?})
"""
        # Ruby source and secrets travel over stdin, not command-line or stdout logs.
        ruby = ruby.replace('JSON.parse(STDIN.read)', 'JSON.parse(' + json.dumps(payload) + ')')
        output = command('docker', 'exec', '-i', config['name'],
                         'gitlab-rails', 'runner', '-', input=ruby, timeout=240)
        result = json.loads(output.splitlines()[-1])
        if result['admin']:
            raise RuntimeError('Learner must not be an administrator.')
        config['api_token'] = result['token']
        save(config)
    if not gateway_healthy(config):
        log = open(STATE / 'gateway.log', 'a', encoding='utf-8')
        process = subprocess.Popen([sys.executable, str(Path(__file__)), 'serve'],
                                   stdout=log, stderr=log,
                                   env={**os.environ,'MQ3_GITLAB_STATE':str(STATE)},
                                   creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
        config['gateway_pid'] = process.pid
        save(config)
        for _ in range(30):
            if gateway_healthy(config):
                break
            time.sleep(1)
        else:
            raise RuntimeError('Local gateway did not start; see .state/gateway.log')
    projects = api(config, 'GET', '/projects', params={'owned': 'true', 'search': 'mq-mr-practice'})
    if not any(p['path'] == 'mq-mr-practice' for p in projects):
        api(config, 'POST', '/projects', json=dict(name='mq-mr-practice', visibility='public',
            initialize_with_readme=True, default_branch='main', builds_access_level='disabled'))
    print('Ready: ' + config['url'] + '/' + config['username'] + '/mq-mr-practice', flush=True)


class Tokens(html.parser.HTMLParser):
    value = None

    def handle_starttag(self, tag, attrs):
        data = dict(attrs)
        if tag == 'meta' and data.get('name') == 'csrf-token':
            self.value = data.get('content')


def serve():
    config = load()
    session = requests.Session()
    upstream = f"http://127.0.0.1:{config['internal_port']}"
    lock = threading.RLock()
    common = {'Host': urlsplit(config['url']).netloc, 'X-Forwarded-Proto': 'http'}
    session.headers.update(common)

    def login():
        response = session.get(upstream + '/users/sign_in', timeout=60)
        parser = Tokens()
        parser.feed(response.text)
        if not parser.value:
            raise RuntimeError('GitLab sign-in CSRF token not found')
        response = session.post(upstream + '/users/sign_in', timeout=60, allow_redirects=False,
                                data={'authenticity_token': parser.value,
                                      'user[login]': config['username'],
                                      'user[password]': config['password'],
                                      'user[remember_me]': '1'},
                                headers={'Origin': config['url'], 'Referer': config['url'] + '/users/sign_in'})
        if response.status_code not in (302, 303) or '/users/sign_in' in response.headers.get('Location', ''):
            raise RuntimeError('Dedicated GitLab learner login failed')

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_args):
            pass

        def handle_request(self):
            allowed_hosts = {urlsplit(config['url']).netloc, f"localhost:{config['port']}"}
            if self.headers.get('Host') not in allowed_hosts:
                self.send_error(403, 'Loopback lab only')
                return
            origin = self.headers.get('Origin')
            if origin and origin not in {config['url'], f"http://localhost:{config['port']}"}:
                self.send_error(403, 'Foreign origin')
                return
            if self.path == '/__mq/health':
                data = b'{"ok":true,"identity":"mq_learner","local_only":true}'
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Length', str(len(data)))
                self.end_headers()
                self.wfile.write(data)
                return
            if self.path.startswith(('/users/sign_in', '/users/sign_out')):
                self.send_response(303)
                self.send_header('Location', '/' + config['username'] + '/mq-mr-practice')
                self.end_headers()
                return
            size = int(self.headers.get('Content-Length', 0))
            if size > 32 * 1024 * 1024 or self.headers.get('Transfer-Encoding'):
                self.send_error(413, 'Exercise request too large')
                return
            body = self.rfile.read(size) if size else None
            excluded = {'host', 'cookie', 'authorization', 'private-token', 'connection',
                        'accept-encoding', 'content-length', 'transfer-encoding'}
            headers = {k: v for k, v in self.headers.items() if k.lower() not in excluded}
            headers.update(common)
            if self.path.startswith('/api/v4/'):
                headers['PRIVATE-TOKEN'] = load()['api_token']
            if '.git/' in urlsplit(self.path).path:
                credentials = base64.b64encode((config['username'] + ':' + config['password']).encode()).decode()
                headers['Authorization'] = 'Basic ' + credentials
            try:
                with lock:
                    if not session.cookies:
                        login()
                    response = session.request(self.command, upstream + self.path, headers=headers,
                                               data=body, allow_redirects=False, timeout=120)
                    if '/users/sign_in' in response.headers.get('Location', ''):
                        login()
                        response = session.request(self.command, upstream + self.path, headers=headers,
                                                   data=body, allow_redirects=False, timeout=120)
                self.send_response(response.status_code)
                for key, value in response.headers.items():
                    if key.lower() not in {'set-cookie', 'content-length', 'content-encoding',
                                           'transfer-encoding', 'connection'}:
                        self.send_header(key, value)
                self.send_header('Content-Length', str(len(response.content)))
                self.end_headers()
                if self.command != 'HEAD':
                    self.wfile.write(response.content)
            except (requests.RequestException, RuntimeError):
                self.send_error(502, 'Local GitLab is not ready')

        do_GET = do_POST = do_PUT = do_PATCH = do_DELETE = do_HEAD = handle_request

    ThreadingHTTPServer(('127.0.0.1', config['port']), Handler).serve_forever()


def verify():
    config = load()
    who = api(config, 'GET', '/user')
    assert who['username'] == config['username'] and not who.get('is_admin', False)
    project = api(config, 'POST', '/projects', json=dict(
        name='mq-verify-' + time.strftime('%Y%m%d%H%M%S'), visibility='public',
        initialize_with_readme=True, default_branch='main', builds_access_level='disabled'))
    workspace = STATE / project['path']
    env = {**os.environ, 'GIT_TERMINAL_PROMPT': '0', 'GIT_CONFIG_NOSYSTEM': '1'}
    def git(*args):
        return command('git', '-c', 'credential.helper=', *args, cwd=workspace, env=env, timeout=120)
    command('git', '-c', 'credential.helper=', 'clone', project['http_url_to_repo'], str(workspace), env=env, timeout=120)
    git('config', 'user.name', 'MQ learner')
    git('config', 'user.email', 'mq-learner@example.invalid')
    git('switch', '-c', 'feature')
    (workspace / 'memo.txt').write_text('Review this change before merging.\n', encoding='utf-8')
    git('add', 'memo.txt')
    git('commit', '-m', 'Write the shared memo')
    git('push', '-u', 'origin', 'feature')
    path = f"/projects/{project['id']}/merge_requests"
    mr = api(config, 'POST', path, json=dict(source_branch='feature', target_branch='main', title='Review the memo'))
    diffs = api(config, 'GET', path + f"/{mr['iid']}/diffs")
    assert any('Review this change' in item['diff'] for item in diffs)
    for _ in range(30):
        current = api(config, 'GET', path + f"/{mr['iid']}")
        if current.get('detailed_merge_status') == 'mergeable':
            break
        time.sleep(2)
    merged = api(config, 'PUT', path + f"/{mr['iid']}/merge", json={'sha': current['sha']})
    assert merged['state'] == 'merged'
    git('switch', 'main')
    git('pull', '--ff-only')
    assert 'Review this change' in (workspace / 'memo.txt').read_text(encoding='utf-8')
    web = requests.get(merged['web_url'], timeout=60)
    assert web.ok and '/users/sign_in' not in web.url and 'Review the memo' in web.text
    rejected = requests.post(config['url'] + '/api/v4/projects',
                             headers={'Origin': 'https://example.com'}, json={'name':'blocked'}, timeout=10)
    assert rejected.status_code == 403
    result = dict(verified=True, learner_login_required=False, shared_identity=who['username'],
                  clone_push=True, mr_created=True, diff_read=True, merged=True, local_pull=True,
                  mr_url=merged['web_url'], foreign_origin_blocked=True)
    (STATE / 'verification.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result), flush=True)


def install_cli():
    import hashlib
    import io
    import platform
    import tarfile
    import zipfile
    c = load()
    system = {'win32':'windows','darwin':'darwin','linux':'linux'}[sys.platform]
    arch = 'arm64' if platform.machine().lower() in ('arm64','aarch64') else 'amd64'
    name = 'glab.exe' if system == 'windows' else 'glab'
    folder = STATE / 'cli'
    executable = folder / name
    if not executable.exists():
        folder.mkdir(exist_ok=True)
        version = '1.126.0'
        filename = f"glab_{version}_{system}_{arch}." + ('zip' if system == 'windows' else 'tar.gz')
        base = f'https://gitlab.com/gitlab-org/cli/-/releases/v{version}/downloads/'
        checksums = requests.get(base + 'checksums.txt',timeout=120)
        checksums.raise_for_status()
        expected = next(line.split()[0] for line in checksums.text.splitlines() if line.split()[-1].lstrip('*') == filename)
        download = requests.get(base + filename,timeout=300)
        download.raise_for_status()
        if hashlib.sha256(download.content).hexdigest() != expected:
            raise RuntimeError('Official glab archive checksum mismatch')
        if system == 'windows':
            with zipfile.ZipFile(io.BytesIO(download.content)) as archive:
                entry = next(x for x in archive.namelist() if x.rsplit('/',1)[-1] == name)
                executable.write_bytes(archive.read(entry))
        else:
            with tarfile.open(fileobj=io.BytesIO(download.content),mode='r:gz') as archive:
                entry = next(x for x in archive.getmembers() if x.isfile() and x.name.rsplit('/',1)[-1] == name)
                executable.write_bytes(archive.extractfile(entry).read())
            executable.chmod(0o700)
    c['glab_dir'] = str(folder)
    save(c)
    print('Official glab CLI ready.',flush=True)


def runner():
    c = load()
    name = c['name'] + '-runner'
    network = c['name'] + '-ci'
    if owned(c['name'], 'local-gitlab-lab') is None:
        raise RuntimeError('Start the local GitLab lab before its runner')
    existing_runner = owned(name, 'gitlab-ci')
    inspected = subprocess.run(['docker','network','inspect',network],capture_output=True,text=True,encoding='utf-8',errors='replace')
    if inspected.returncode:
        command('docker','network','create','--label','mq3.role=gitlab-ci',network)
    elif (json.loads(inspected.stdout)[0].get('Labels') or {}).get('mq3.role') != 'gitlab-ci':
        raise RuntimeError('Refusing to use a network not owned by this lab: ' + network)
    networks = json.loads(command('docker','inspect',c['name']))[0]['NetworkSettings']['Networks']
    if network not in networks:
        command('docker','network','connect',network,c['name'])
    if not c.get('runner_token'):
        ruby = "r=Ci::Runner.create!(runner_type: 'instance_type',description: 'MQ local Docker runner',run_untagged: true,locked: false); puts JSON.generate({token:r.token})"
        output = command('docker','exec',c['name'],'gitlab-rails','runner',ruby,timeout=240)
        c['runner_token'] = json.loads(output.splitlines()[-1])['token']
        save(c)
    path=STATE/'runner.toml'
    if path.exists() and 'container_labels' not in path.read_text(encoding='utf-8'):
        text=path.read_text(encoding='utf-8').replace('[runners.docker]',f'[runners.docker]\n    container_labels = {{ "mq3.gitlab.owner" = "{c["name"]}" }}')
        path.write_text(text,encoding='utf-8',newline='\n')
    if existing_runner is not None:
        command('docker','start',name)
        print('Local Docker runner ready.',flush=True)
        return
    command('docker','pull','gitlab/gitlab-runner:alpine',timeout=1200)
    image = json.loads(command('docker','image','inspect','gitlab/gitlab-runner:alpine'))[0]['RepoDigests'][0]
    c['runner_image'] = image
    configuration = f'''concurrent = 1
check_interval = 2
[[runners]]
  name = "MQ local CI"
  url = "http://{c['name']}"
  clone_url = "http://{c['name']}"
  token = "{c['runner_token']}"
  executor = "docker"
  [runners.docker]
    container_labels = {{ "mq3.gitlab.owner" = "{c['name']}" }}
    image = "alpine:3.22"
    network_mode = "{network}"
    privileged = false
    disable_cache = true
    pull_policy = "if-not-present"
    allowed_pull_policies = ["if-not-present"]
    allowed_images = ["alpine:3.22"]
    allowed_services = ["mq-no-services.invalid/*:*"]
    memory = "256m"
    cpus = "1"
    volumes = []
'''
    path = STATE / 'runner.toml'
    path.write_text(configuration,encoding='utf-8',newline='\n')
    command('docker','run','-d','--name',name,'--label','mq3.role=gitlab-ci',
            '--network',network,'--restart','no',
            '--mount',f'type=bind,src={path},dst=/etc/gitlab-runner/config.toml,readonly',
            '--mount','type=bind,src=/var/run/docker.sock,dst=/var/run/docker.sock',image,timeout=120)
    save(c)
    print('Local Docker runner ready.',flush=True)


def stop():
    config = load()
    runner_name = config['name'] + '-runner'
    # Validate every container this command may touch before changing anything.
    lab = owned(config['name'], 'local-gitlab-lab')
    runner_container = owned(runner_name, 'gitlab-ci')
    if os.name == 'nt' and config.get('gateway_pid'):
        # Verify the PID belongs to this gateway before terminating it.
        check = command('powershell', '-NoProfile', '-Command',
            f"(Get-CimInstance Win32_Process -Filter 'ProcessId = {int(config['gateway_pid'])}').CommandLine")
        if str(Path(__file__)) in check and 'serve' in check:
            command('taskkill', '/PID', str(config['gateway_pid']), '/F')
    elif config.get('gateway_pid'):
        import signal
        process=subprocess.run(['ps','-p',str(config['gateway_pid']),'-o','args='],capture_output=True,text=True)
        if str(Path(__file__)) in process.stdout and 'serve' in process.stdout:
            os.kill(config['gateway_pid'],signal.SIGTERM)
    if runner_container is not None:
        command('docker','stop',runner_name,timeout=120)
    jobs=command('docker','ps','-aq','--filter','label=mq3.gitlab.owner='+config['name']).splitlines()
    for job in jobs:
        if len(job) in (12,64) and all(c in '0123456789abcdef' for c in job):
            command('docker','rm','-f',job,timeout=60)
    if lab is not None:
        command('docker', 'stop', config['name'], timeout=120)
    print('Local lab stopped; its volumes are preserved.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['start', 'serve', 'verify', 'status', 'stop', 'runner','install_cli','ready_json'])
    action = parser.parse_args().action
    if action == 'ready_json':
        c = load()
        print(json.dumps({k:c.get(k) for k in ('name','url','username','glab_dir')}))
    elif action == 'status':
        c = load()
        print(json.dumps({k: c[k] for k in ('name','url','image')}, indent=2))
    else:
        globals()[action]()

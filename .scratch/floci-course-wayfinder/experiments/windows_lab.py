"""Disposable Windows -> DIND -> Floci experiment. Never addresses real AWS.
Python stdlib only. API subprocess environment replaces all AWS credential paths.
All Docker mutations target named run-owned resources or the empty inner daemon.
"""
import json, os, pathlib, subprocess, time, traceback, datetime, tempfile

ROOT = pathlib.Path(__file__).resolve().parent
RUN = 'mq-floci-win-' + datetime.datetime.now().strftime('%Y%m%d%H%M%S')
OUT = ROOT / RUN
OUT.mkdir()
EVENTS = []
DIND = 'docker@sha256:ecac43e78380d9b9d3bd24f0ab42b370f6391a1a06a66065c10a00b9d6d57a3e'
FLOCI = 'floci/floci@sha256:5ee85db604c4aa74ac76e07ea5cc83086f37bb472bf3dbb97e34019e48efae9c'
ALPINE = 'public.ecr.aws/docker/library/alpine@sha256:f59abe656b692d901e184be3445e084786602108599d2a51d229c0f5a48c71bf'
AWS = r'C:\Program Files\Amazon\AWSCLIV2\aws.exe'
PORT = '45669'
ENV = os.environ.copy()
for key in list(ENV):
    if key.startswith('AWS_'): del ENV[key]
EMPTY = OUT / 'empty-aws-config'
EMPTY.write_text('')
ENV.update(AWS_ACCESS_KEY_ID='test', AWS_SECRET_ACCESS_KEY='test', AWS_DEFAULT_REGION='us-east-1',
           AWS_CONFIG_FILE=str(EMPTY), AWS_SHARED_CREDENTIALS_FILE=str(EMPTY), AWS_EC2_METADATA_DISABLED='true', AWS_PAGER='')

def cmd(args, timeout=120, check=True, label=None):
    start = time.time()
    r = subprocess.run(args, env=ENV, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=timeout)
    e = dict(label=label, argv=args, rc=r.returncode, seconds=round(time.time()-start, 3), stdout=r.stdout, stderr=r.stderr)
    EVENTS.append(e)
    (OUT/'events.json').write_text(json.dumps(EVENTS, ensure_ascii=False, indent=2), encoding='utf-8')
    if check and r.returncode: raise RuntimeError(f'{label or args[:3]}: {r.stderr[-800:]}')
    return r

def docker(*args, **kw): return cmd(['docker', *args], **kw)
def inner(*args, **kw): return docker('exec', RUN, 'docker', *args, **kw)
def api(action, *args, check=True, label=None):
    r = cmd([AWS, '--endpoint-url', f'http://127.0.0.1:{PORT}', '--region', 'us-east-1', '--output', 'json', '--cli-connect-timeout', '5', '--cli-read-timeout', '30', 'ec2', action, *args], check=check, label=label or action)
    return json.loads(r.stdout) if r.returncode == 0 and r.stdout.strip() else {'error': r.stderr, 'rc': r.returncode}

def wait(fn, seconds=90):
    end=time.time()+seconds
    while time.time()<end:
        try:
            val=fn()
            if val: return val
        except Exception: pass
        time.sleep(2)
    raise TimeoutError('readiness timeout')

def save(name, obj): (OUT/(name+'.json')).write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8')

def bootstrap():
    save('host-before', {
        'containers':docker('ps','-aq','--no-trunc').stdout.split(),
        'networks':docker('network','ls','--format','{{json .}}').stdout.splitlines(),
        'volumes':docker('volume','ls','--format','{{json .}}').stdout.splitlines(),
        'version':json.loads(docker('version','--format','{{json .}}').stdout),
        'image':json.loads(docker('image','inspect',FLOCI).stdout),
        'dind_image':json.loads(docker('image','inspect',DIND).stdout)})
    docker('network','create','--label',f'mq.lab={RUN}',RUN)
    docker('volume','create','--label',f'mq.lab={RUN}',RUN)
    docker('run','-d','--name',RUN,'--label',f'mq.lab={RUN}','--privileged','--cgroupns=host','--cpus','4','--memory','6g','--pids-limit','2048','--network',RUN,'-p',f'127.0.0.1:{PORT}:4566','-v',f'{RUN}:/var/lib/docker','--entrypoint','dockerd',DIND,'--host=unix:///var/run/docker.sock','--storage-driver=overlay2')
    wait(lambda: inner('info',check=False).returncode==0)
    save('outer-inspect',json.loads(docker('inspect',RUN).stdout))
    save('inner-version',json.loads(inner('version','--format','{{json .}}').stdout))
    inner('pull',FLOCI,timeout=240)
    inner('pull',ALPINE,timeout=180)
    inner('tag',ALPINE,'public.ecr.aws/docker/library/alpine:latest')
    save('alpine-image',json.loads(inner('image','inspect','public.ecr.aws/docker/library/alpine:latest').stdout))

def start_floci(enforcement=False):
    inner('run','-d','--name','floci','--label',f'mq.lab={RUN}','--cpus','2','--memory','2g','--pids-limit','512','--network','host','-v','/var/run/docker.sock:/var/run/docker.sock','-e',f'FLOCI_DOCKER_RESOURCE_NAMESPACE={RUN}','-e','FLOCI_STORAGE_MODE=memory','-e','FLOCI_SERVICES_EC2_PUBLISH_SECURITY_GROUP_PORTS=false','-e',f'FLOCI_NETWORK_SECURITY_GROUP_ENFORCEMENT_ENABLED={str(enforcement).lower()}',FLOCI)
    wait(lambda: api('describe-vpcs',check=False).get('Vpcs') is not None)

def cleanup():
    # The run owns its complete empty-at-bootstrap inner daemon. Outer labels must match.
    if docker('inspect',RUN,check=False).returncode==0:
        save('inner-final-inventory',{'containers':inner('ps','-a','--no-trunc','--format','{{json .}}',check=False).stdout.splitlines(),'networks':inner('network','ls','--format','{{json .}}',check=False).stdout.splitlines()})
        inner('logs','floci',check=False,label='floci-final-log')
        obj=json.loads(docker('inspect',RUN).stdout)[0]
        assert obj['Config']['Labels'].get('mq.lab')==RUN
        docker('rm','-f',RUN)
    for kind in ['volume','network']:
        r=docker(kind,'inspect',RUN,check=False)
        if r.returncode==0:
            assert json.loads(r.stdout)[0]['Labels'].get('mq.lab')==RUN
            docker(kind,'rm',RUN)
    save('host-after',{'containers':docker('ps','-aq','--no-trunc').stdout.split(),'networks':docker('network','ls','--format','{{json .}}').stdout.splitlines(),'volumes':docker('volume','ls','--format','{{json .}}').stdout.splitlines()})

if __name__=='__main__':
    print(str(OUT),flush=True)
    failed=False
    try:
        bootstrap()
        start_floci()
        print('BOOTSTRAP_READY',flush=True)
        # The matrix module is imported after isolation is verified.
        import windows_matrix
        windows_matrix.run(__import__('__main__'))
    except BaseException:
        failed=True
        save('fatal',{'traceback':traceback.format_exc()})
        print(traceback.format_exc(),flush=True)
    finally:
        cleanup()
        print('CLEANED',flush=True)
    if failed: raise SystemExit(1)

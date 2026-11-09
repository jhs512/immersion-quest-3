"""Read-only evidence checks; no runtime resource creation."""
import pathlib,json,re,socket,subprocess
ROOT=pathlib.Path(__file__).resolve().parent
results=[]
for d in sorted(ROOT.glob('mq-floci-db-*')):
    events=json.loads((d/'events.json').read_text(encoding='utf8'))
    aws=[e for e in events if e['argv'][0].endswith('aws.exe')]
    for e in aws:
        a=e['argv'];assert a[a.index('--endpoint-url')+1]=='http://127.0.0.1:45671'
        assert a[a.index('--region')+1]=='us-east-1'
    before=json.loads((d/'host-before.json').read_text());after=json.loads((d/'host-after.json').read_text());assert before==after
    outer=json.loads((d/'outer-inspect.json').read_text())[0]
    bindings=outer['HostConfig']['PortBindings'];assert set(bindings)=={'4566/tcp'}
    assert bindings['4566/tcp']==[{'HostIp':'127.0.0.1','HostPort':'45671'}]
    mounts=outer['HostConfig']['Binds'];assert mounts==[d.name+':/var/lib/docker']
    assert outer['Config']['Labels']['mq.lab']==d.name
    results.append({'run':d.name,'awsCalls':len(aws),'loopbackOnly':True,'hostInventoryEqual':True,'onlyOwnedVolumeMounted':True,'fatal':(d/'fatal.json').exists(),'serviceFailures':[p.name for p in d.glob('*-failure.json')]})
live={}
for kind,args in [('containers',['ps','-a','--filter','label=mq.lab','--format','{{.Names}}']),('networks',['network','ls','--filter','label=mq.lab','--format','{{.Name}}']),('volumes',['volume','ls','--filter','label=mq.lab','--format','{{.Name}}'])]:
    r=subprocess.run(['docker',*args],capture_output=True,text=True,check=True);owned=[x for x in r.stdout.splitlines() if x.startswith('mq-floci-db-')];assert not owned;live[kind]=owned
s=socket.socket();assert s.connect_ex(('127.0.0.1',45671))!=0;s.close()
credential_findings=[]
for p in ROOT.rglob('*'):
    if p.is_file() and p.suffix in {'.json','.py','.md','.txt'}:
        txt=p.read_text(encoding='utf8')
        if re.search(r'\b(?:AKIA|ASIA)[A-Z0-9]{16}\b|-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----',txt):credential_findings.append(str(p.relative_to(ROOT)))
assert not credential_findings
out={'runs':results,'liveOwnedResources':live,'portReleased':True,'credentialPatternFindings':credential_findings,'scope':'AWS endpoint argv + mounted paths + inventory + known credential patterns, not a proof of arbitrary-secret absence'}
(ROOT/'audit.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(out,ensure_ascii=False))

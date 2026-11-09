"""Audit raw evidence without printing credential-shaped values."""
import json, pathlib, re, subprocess

ROOT=pathlib.Path(__file__).resolve().parent
RULES={
    'aws-access-key':r'\b(?:AKIA|ASIA)[A-Z0-9]{16}\b',
    'private-key':r'-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----',
    'github-token':r'\b(?:ghp_|github_pat_)[A-Za-z0-9_]{20,}',
    'anthropic-token':r'sk-ant-[A-Za-z0-9_-]{10,}',
    'google-oauth':r'ya29\.[A-Za-z0-9_-]{20,}',
}
report={'runs':[],'secretPatternMatches':[],'awsEndpointViolations':[]}
for run in sorted(ROOT.glob('mq-floci-win-*')):
    for f in run.glob('*.json'):
        s=f.read_text(encoding='utf-8')
        for pattern,regex in RULES.items():
            count=len(re.findall(regex,s))
            if count:report['secretPatternMatches'].append({'run':run.name,'file':f.name,'pattern':pattern,'count':count})
    events=json.loads((run/'events.json').read_text(encoding='utf-8'))
    api=[e for e in events if e['argv'][0].endswith('aws.exe')]
    for e in api:
        args=e['argv'];idx=args.index('--endpoint-url') if '--endpoint-url' in args else -1
        if idx<0 or args[idx+1]!='http://127.0.0.1:45669':
            report['awsEndpointViolations'].append({'run':run.name,'action':e['label']})
    cleanup=None
    if (run/'host-after.json').exists():
        before=json.loads((run/'host-before.json').read_text(encoding='utf-8'))
        after=json.loads((run/'host-after.json').read_text(encoding='utf-8'))
        cleanup={k:{'added':[x for x in after[k] if x not in before[k]],'removed':[x for x in before[k] if x not in after[k]]} for k in ['containers','networks','volumes']}
    report['runs'].append({'run':run.name,'events':len(events),'awsCalls':len(api),'fatal':(run/'fatal.json').exists(),'cleanup':cleanup})
report['liveOwned']={}
for kind,args in {
    'containers':['ps','-aq','--filter','label=mq.lab'],
    'networks':['network','ls','-q','--filter','label=mq.lab'],
    'volumes':['volume','ls','-q','--filter','label=mq.lab'],
}.items():
    r=subprocess.run(['docker',*args],capture_output=True,text=True,check=True)
    report['liveOwned'][kind]=r.stdout.split()
(ROOT/'audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False))

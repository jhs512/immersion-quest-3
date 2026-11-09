"""Recompute assertions from retained evidence without Docker or AWS access."""
import json,pathlib,sys
p=pathlib.Path(sys.argv[1]);load=lambda f:json.loads((p/(f+'.json')).read_text(encoding='utf-8'))
before,after=load('host-before'),load('host-after')
def canonical(rows):return sorted(json.dumps(json.loads(x),sort_keys=True) for x in rows)
audit={'baseline_containers_preserved':sorted(before['containers'])==sorted(after['containers']),
       'baseline_networks_preserved':canonical(before['networks'])==canonical(after['networks']),
       'baseline_volumes_preserved':canonical(before['volumes'])==canonical(after['volumes'])}
outer=load('outer-inspect')[0]
audit['outer_only_loopback_api']=outer['HostConfig']['PortBindings']=={'4566/tcp':[{'HostIp':'127.0.0.1','HostPort':'45670'}]}
audit['no_host_socket_mount']=all(x['Source']!='/var/run/docker.sock' for x in outer['Mounts'])
audit['cgroup_host']=outer['HostConfig']['CgroupnsMode']=='host'
if (p/'checks.json').exists():
    c=load('checks');audit['matrix_passed']=sum(x['passed'] for x in c);audit['matrix_total']=len(c);audit['matrix_failed']=[x['name'] for x in c if not x['passed']]
events=load('events');aws=[x for x in events if x['argv'][0].endswith('aws.exe')]
audit['all_host_aws_explicit_loopback']=all(x['argv'][x['argv'].index('--endpoint-url')+1]=='http://127.0.0.1:45670' for x in aws)
(p/'audit.json').write_text(json.dumps(audit,indent=2),encoding='utf-8');print(json.dumps(audit,indent=2))

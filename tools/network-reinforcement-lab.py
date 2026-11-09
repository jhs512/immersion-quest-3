"""Run owned Docker Desktop networking experiments; never alter host routes/DNS.

Evidence is written as JSON, including negative controls and cleanup results.
This is a teacher validation harness, not a claim of integrated student grading.
"""
from __future__ import annotations

import argparse
import ipaddress
import json
from pathlib import Path
import subprocess
import tempfile
import time
import uuid


WEB = '''import http.server, json, os, sys
port=int(sys.argv[2])
open('/tmp/http-%s.pid'%port,'w').write(str(os.getpid()))
class Handler(http.server.BaseHTTPRequestHandler):
 def do_GET(self):
  body=json.dumps(dict(server=os.environ['HOSTNAME'],peer=self.client_address[0],local=self.connection.getsockname()[0])).encode()
  self.send_response(200); self.send_header('Content-Length',str(len(body))); self.end_headers(); self.wfile.write(body)
 def log_message(self,*args): pass
http.server.ThreadingHTTPServer((sys.argv[1],port),Handler).serve_forever()
'''


class Lab:
    def __init__(self, output: Path, block: str | None = None):
        self.output = output
        self.requested_block = block
        self.tag = 'iq-net-' + uuid.uuid4().hex[:10]
        self.image = 'immersion-network-lab:alpine-3.22'
        self.containers: list[str] = []
        self.networks: list[str] = []
        self.report = {'run': self.tag, 'platform': 'Docker Desktop Linux containers',
                       'commands': [], 'checks': [], 'cleanup': [],
                       'limitations': ['Windows host only; macOS not executed',
                                       'NAT outside observer uses private lab addresses, not public Internet',
                                       'Teacher harness; student lifecycle/grading not integrated']}

    def docker(self, *args: str, ok=True, timeout=60):
        p = subprocess.run(['docker', *map(str, args)], capture_output=True,
                           text=True, encoding='utf-8', errors='replace', timeout=timeout)
        self.report['commands'].append(dict(args=list(args), returncode=p.returncode,
                                            stdout=p.stdout, stderr=p.stderr))
        self.save()
        if ok and p.returncode:
            raise RuntimeError(f'docker {args[0]} failed: {p.stderr[-1500:]}')
        return p

    def save(self):
        self.output.parent.mkdir(parents=True, exist_ok=True)
        self.output.write_text(json.dumps(self.report, ensure_ascii=False, indent=2), encoding='utf-8')

    def check(self, name, condition, evidence):
        self.report['checks'].append(dict(name=name, passed=bool(condition), evidence=evidence))
        self.save()
        print(('PASS ' if condition else 'FAIL ') + name, flush=True)
        if not condition:
            raise AssertionError(name)

    def net(self, role, subnet, internal=False, gateway=None):
        name = self.tag + '-' + role
        args = ['network', 'create', '--label', 'immersion.network-lab=' + self.tag,
                '--subnet', subnet]
        if internal:
            args += ['--internal']
        if gateway:
            args += ['--gateway', gateway]
        self.docker(*args, name)
        self.networks.append(name)
        return name

    def container(self, role, net, address, admin=False, dns=None, image=None, command=None, forward=False):
        name = self.tag + '-' + role
        args = ['create', '--name', name, '--label', 'immersion.network-lab=' + self.tag,
                '--network', net, '--ip', address]
        if admin:
            args += ['--cap-add', 'NET_ADMIN']
        if forward:
            args += ['--sysctl', 'net.ipv4.ip_forward=1']
        if dns:
            args += ['--dns', dns]
        args += [image or self.image] + (command or ['sleep', 'infinity'])
        self.docker(*args)
        self.containers.append(name)
        return name

    def start(self, name):
        self.docker('start', name)

    def ex(self, name, *args, ok=True):
        return self.docker('exec', name, *args, ok=ok)

    def shell(self, name, command, ok=True):
        return self.ex(name, 'sh', '-c', command, ok=ok)

    def http(self, client, address, port=8080, ok=True):
        return self.ex(client, 'curl', '--noproxy', '*', '-fsS', '--connect-timeout', '2',
                       '--max-time', '4', f'http://{address}:{port}/', ok=ok)

    def server(self, name, bind='0.0.0.0', port=8080):
        self.docker('exec', '-d', name, 'python3', '/lab/web.py', bind, str(port))
        # Poll actual readiness, not an assumed startup duration.
        for _ in range(30):
            result = self.http(name, '127.0.0.1', port, ok=False)
            if result.returncode == 0:
                return
            time.sleep(.1)
        raise RuntimeError('HTTP server did not become ready')

    def run(self):
        self.report['engine'] = self.docker('info', '--format', '{{.ServerVersion}} / {{.OSType}} / {{.Architecture}}').stdout.strip()
        existing = self.docker('network', 'ls', '-q').stdout.split()
        occupied = []
        if existing:
            for network in json.loads(self.docker('network', 'inspect', *existing).stdout):
                for entry in network['IPAM']['Config'] or []:
                    if entry.get('Subnet'):
                        occupied.append(ipaddress.ip_network(entry['Subnet']))
        block = next((ipaddress.ip_network(f'172.{second}.{third}.0/22')
                      for second in range(29, 16, -1) for third in range(240, 196, -4)
                      if not any(ipaddress.ip_network(f'172.{second}.{third}.0/22').overlaps(n)
                                 for n in occupied if n.version == 4)), None)
        if block is None:
            raise RuntimeError('No unused private experiment block')
        if self.requested_block:
            requested=ipaddress.ip_network(self.requested_block)
            if requested.version!=4 or requested.prefixlen!=22 or not requested.subnet_of(ipaddress.ip_network('172.16.0.0/12')):
                raise ValueError('Experiment block must be a private 172.16.0.0/12 IPv4 /22')
            if any(requested.overlaps(n) for n in occupied if n.version==4):
                raise ValueError('Requested experiment block overlaps an existing Docker network')
            block=requested
        subnets = list(block.subnets(new_prefix=24))
        addr = lambda n, host: str(subnets[n].network_address + host)
        self.report['address_block'] = str(block)
        with tempfile.TemporaryDirectory(prefix=self.tag) as tmp:
            tmp = Path(tmp)
            (tmp / 'Dockerfile').write_text(
                'FROM alpine:3.22\nRUN apk add --no-cache python3 iproute2 iptables bind-tools curl\n'
                'COPY web.py /lab/web.py\n', encoding='utf-8')
            (tmp / 'web.py').write_text(WEB, encoding='utf-8')
            self.docker('build', '-t', self.image, str(tmp), timeout=240)
            self.report['lab_image'] = json.loads(self.docker('image', 'inspect', self.image).stdout)[0]['Id']
            self.docker('pull', 'coredns/coredns:1.12.0', timeout=180)
            self.report['dns_image'] = json.loads(self.docker('image', 'inspect', 'coredns/coredns:1.12.0').stdout)[0]['Id']
            main = self.net('main', str(subnets[0]))
            web_a = self.container('web-a', main, addr(0, 130), admin=True)
            web_b = self.container('web-b', main, addr(0, 140))
            self.start(web_a); self.start(web_b)
            self.server(web_a); self.server(web_b)

            # Actual authoritative DNS, distinct from Docker's embedded forwarder.
            core = tmp / 'Corefile'
            core.write_text('memo.test:53 {\n file /zone memo.test\n errors\n log\n}\n', encoding='utf-8')
            zone = tmp / 'zone'
            def write_zone(ip, serial, ttl=0):
                zone.write_text(f'$ORIGIN memo.test.\n$TTL {ttl}\n@ IN SOA ns.memo.test. hostmaster.memo.test. {serial} 60 60 60 0\n@ IN NS ns.memo.test.\nns IN A {addr(0,53)}\n@ IN A {ip}\n', encoding='utf-8')
            write_zone(addr(0, 130), 1)
            dns = self.container('dns', main, addr(0, 53), image='coredns/coredns:1.12.0', command=['-conf', '/Corefile'])
            self.docker('cp', str(core), dns + ':/Corefile')
            self.docker('cp', str(zone), dns + ':/zone')
            self.start(dns)
            client = self.container('client', main, addr(0, 10), admin=True, dns=addr(0, 53))
            self.start(client)
            iface = json.loads(self.ex(client, 'ip', '-j', 'route', 'get', addr(0,130)).stdout)[0]['dev']
            before = json.loads(self.ex(client, 'ip', '-j', 'route', 'get', addr(0,130)).stdout)[0]
            self.check('same /24 selects direct route', 'gateway' not in before, before)
            self.ex(client, 'ip', 'addr', 'del', addr(0,10) + '/24', 'dev', iface)
            self.ex(client, 'ip', 'addr', 'add', addr(0,10) + '/25', 'dev', iface)
            # Removing the interface's last address can also remove its default
            # route. Restore that independent variable before comparing masks.
            self.ex(client, 'ip', 'route', 'replace', 'default', 'via', addr(0,1))
            after = json.loads(self.ex(client, 'ip', '-j', 'route', 'get', addr(0,130)).stdout)[0]
            outcome = self.http(client, addr(0,130), ok=False)
            self.check('/25 changes chosen path without equating mask with failure',
                       after.get('gateway') == addr(0,1), dict(route=after, http_returncode=outcome.returncode))
            self.ex(client, 'ip', 'addr', 'del', addr(0,10) + '/25', 'dev', iface)
            self.ex(client, 'ip', 'addr', 'add', addr(0,10) + '/24', 'dev', iface)
            self.ex(client, 'ip', 'route', 'replace', 'default', 'via', addr(0,1))
            self.ex(client, 'ip', 'route', 'add', str(subnets[0].network_address+128)+'/25', 'via', addr(0,1))
            specific = json.loads(self.ex(client, 'ip', '-j', 'route', 'get', addr(0,130)).stdout)[0]
            general = json.loads(self.ex(client, 'ip', '-j', 'route', 'get', addr(0,20)).stdout)[0]
            fallback = json.loads(self.ex(client, 'ip', '-j', 'route', 'get', '192.0.2.50').stdout)[0]
            self.check('longest matching route and default', specific.get('gateway') == addr(0,1)
                       and 'gateway' not in general and fallback.get('gateway') == addr(0,1),
                       dict(specific=specific, general=general, default=fallback))
            self.ex(client, 'ip', 'route', 'del', str(subnets[0].network_address+128)+'/25')
            self.ex(client, 'ip', 'route', 'del', 'default')
            direct = self.http(client, addr(0,130))
            missing = self.ex(client, 'ip', '-j', 'route', 'get', '192.0.2.50', ok=False)
            self.check('removing default preserves direct subnet access', direct.returncode == 0 and missing.returncode != 0, missing.stderr)
            self.ex(client, 'ip', 'route', 'add', 'default', 'via', addr(0,1))

            web_iface = json.loads(self.ex(web_a, 'ip', '-j', 'route', 'get', addr(0,10)).stdout)[0]['dev']
            self.ex(web_a, 'ip', 'addr', 'add', addr(0,132)+'/24', 'dev', web_iface)
            identities = [json.loads(self.http(client, addr(0,n)).stdout) for n in (130,132)]
            self.check('two addresses on one interface reach same server', identities[0]['server'] == identities[1]['server'],
                       dict(responses=identities, interfaces=json.loads(self.ex(web_a,'ip','-j','addr').stdout)))
            self.server(web_a, '127.0.0.1', 8081)
            local = self.http(web_a, '127.0.0.1',8081)
            other_loop = self.http(client, '127.0.0.1',8081,ok=False)
            other_ip = self.http(client, addr(0,130),8081,ok=False)
            self.check('loopback-only server is local to its namespace', local.returncode == 0 and other_loop.returncode != 0 and other_ip.returncode != 0,
                       dict(local=local.returncode,peer_loopback=other_loop.returncode,peer_network_address=other_ip.returncode))
            self.shell(web_a, 'kill "$(cat /tmp/http-8081.pid)"')
            self.server(web_a, '0.0.0.0',8081)
            self.check('changing bind enables peer access without changing destination', self.http(client,addr(0,130),8081).returncode == 0, 'same peer, destination and port; server binding changed')

            def query(expected):
                for _ in range(30):
                    p=self.ex(client,'dig','@'+addr(0,53),'memo.test','A','+short','+time=1','+tries=1',ok=False)
                    if p.returncode == 0 and p.stdout.strip() == expected:
                        return p.stdout.strip()
                    time.sleep(.1)
                raise RuntimeError('authoritative DNS answer mismatch')
            query(addr(0,130))
            first=json.loads(self.http(client,'memo.test').stdout)
            write_zone(addr(0,140),2)
            self.docker('cp',str(zone),dns+':/zone'); self.docker('restart',dns)
            query(addr(0,140))
            second=json.loads(self.http(client,'memo.test').stdout)
            self.check('actual DNS record change selects different server', first['server'] != second['server'],
                       dict(before=first,after=second,resolv_conf=self.ex(client,'cat','/etc/resolv.conf').stdout,
                            authoritative=self.ex(client,'dig','@'+addr(0,53),'memo.test','A').stdout))
            no_name=self.ex(client,'dig','@'+addr(0,53),'missing.memo.test','A').stdout
            dns_ok_closed_port=self.http(client,'memo.test',8099,ok=False)
            self.check('DNS failure differs from resolved name with closed port', 'NXDOMAIN' in no_name and dns_ok_closed_port.returncode != 0,
                       dict(missing_name=no_name,closed_port_returncode=dns_ok_closed_port.returncode))

            # Cache and authority are separate running DNS processes. Observe a
            # still-valid cached answer rather than grading an exact expiry time.
            write_zone(addr(0,140),3,ttl=120)
            self.docker('cp',str(zone),dns+':/zone'); self.docker('restart',dns)
            query(addr(0,140))
            cachefile=tmp/'Cachefile'
            cachefile.write_text('memo.test:53 {\n forward . '+addr(0,53)+'\n cache 300\n}\n',encoding='utf-8')
            cache=self.container('cache',main,addr(0,54),image='coredns/coredns:1.12.0',command=['-conf','/Corefile'])
            self.docker('cp',str(cachefile),cache+':/Corefile');self.start(cache)
            for _ in range(30):
                cached=self.ex(client,'dig','@'+addr(0,54),'memo.test','A','+noall','+answer','+time=1','+tries=1',ok=False)
                if cached.returncode==0 and addr(0,140) in cached.stdout:
                    break
                time.sleep(.1)
            else:
                raise RuntimeError('cache DNS not ready')
            write_zone(addr(0,130),4,ttl=120)
            self.docker('cp',str(zone),dns+':/zone'); self.docker('restart',dns)
            query(addr(0,130))
            stale=self.ex(client,'dig','@'+addr(0,54),'memo.test','A','+noall','+answer').stdout
            self.check('unexpired DNS cache can differ from current authority',
                       addr(0,140) in stale and int(stale.split()[1])>0,
                       dict(cache_before=cached.stdout,cache_after_authority_change=stale,authority=addr(0,130)))
            tcp=self.ex(client,'dig','@'+addr(0,53),'memo.test','A','+tcp','+short').stdout.strip()
            self.check('local DNS also answers TCP queries',tcp==addr(0,130),tcp)

            # Docker --internal adds host bridge isolation rules that can drop
            # traffic destined beyond that subnet before a container router
            # receives it. Use ordinary bridges and control routes inside the
            # owned namespaces instead; no Internet destination is contacted.
            lan=self.net('lan',str(subnets[1]))
            wan=self.net('outside',str(subnets[2]))
            router=self.container('router',lan,addr(1,254),admin=True,forward=True)
            self.docker('network','connect','--ip',addr(2,254),wan,router)
            self.start(router)
            table=json.loads(self.ex(router,'ip','-j','addr').stdout)
            self.check('one host has interfaces in two private networks',
                       all(any(a.get('local')==addr(n,254) for i in table for a in i['addr_info']) for n in (1,2)),table)
            observer=self.container('observer',wan,addr(2,10),admin=True)
            self.start(observer); self.server(observer)
            self.ex(observer,'ip','route','del','default',ok=False)
            self.check('router forwarding configured in container namespace',
                       self.ex(router,'sysctl','-n','net.ipv4.ip_forward').stdout.strip()=='1',
                       'set at container creation; no privileged container or host sysctl change')
            outgoing=json.loads(self.ex(router,'ip','-j','route','get',addr(2,10)).stdout)[0]['dev']
            users=[]
            for host in (10,11):
                c=self.container('user-'+str(host),lan,addr(1,host),admin=True)
                self.start(c)
                self.ex(c,'ip','route','replace','default','via',addr(1,254))
                users.append(c)
            no_nat=self.http(users[0],addr(2,10),ok=False)
            self.ex(router,'iptables','-t','nat','-A','POSTROUTING','-s',str(subnets[1]),'-o',outgoing,'-j','MASQUERADE')
            observed=[json.loads(self.http(c,addr(2,10)).stdout) for c in users]
            self.check('two private clients share translated observer source', no_nat.returncode != 0 and all(o['peer']==addr(2,254) for o in observed),
                       dict(before_nat_returncode=no_nat.returncode,responses=observed,
                            nat=self.ex(router,'iptables','-t','nat','-L','POSTROUTING','-n','-v').stdout,
                            caveat='translated source is still a private lab IP, not a real public IP'))

            small=ipaddress.ip_network(str(subnets[3].network_address+8)+'/29')
            smallnet=self.net('allocation',str(small),gateway=str(small.network_address+1))
            rejected={}
            for role,ip in [('network',small.network_address),('broadcast',small.broadcast_address),('gateway',small.network_address+1),('outside',small.broadcast_address+1)]:
                name=self.tag+'-invalid-'+role
                result=self.docker('create','--name',name,'--network',smallnet,'--ip',str(ip),self.image,'sleep','infinity',ok=False)
                started=None
                if result.returncode==0:
                    self.containers.append(name)
                    started=self.docker('start',name,ok=False)
                rejected[role]=dict(create_returncode=result.returncode,create_stderr=result.stderr,
                                    start_returncode=None if started is None else started.returncode,
                                    start_stderr=None if started is None else started.stderr)
            # Docker's IPAM policy is observed, not used as the definition of IPv4.
            self.report['allocation_ipam_observations']=rejected
            allocated=self.container('valid-host',smallnet,str(small.network_address+2))
            self.start(allocated)
            self.check('usable address allocated in actual /29',self.ex(allocated,'ip','-j','addr').returncode==0,
                       dict(subnet=str(small),network=str(small.network_address),broadcast=str(small.broadcast_address),
                            general_hosts=[str(a) for a in small.hosts()],gateway=str(small.network_address+1),
                            server=str(small.network_address+2),free_if_no_other_reservations=[str(small.network_address+n) for n in range(3,7)]))
            # Free exactly this owned subnet before reusing the same private
            # address for two independent company scenarios in sequence.
            for c in list(self.containers):
                if c==allocated or '-invalid-' in c:
                    self.docker('rm','-f',c);self.containers.remove(c)
            self.docker('network','rm',smallnet);self.networks.remove(smallnet)
            companies=[]
            for company in ('company-a','company-b'):
                net=self.net(company,str(small),gateway=str(small.network_address+1))
                server=self.container(company+'-web',net,str(small.network_address+2))
                caller=self.container(company+'-client',net,str(small.network_address+3))
                self.start(server);self.start(caller);self.server(server)
                companies.append(json.loads(self.http(caller,str(small.network_address+2)).stdout))
                for c in (caller,server):
                    self.docker('rm','-f',c);self.containers.remove(c)
                self.docker('network','rm',net);self.networks.remove(net)
            self.check('same private address reused in independent company labs',
                       companies[0]['local']==companies[1]['local'] and companies[0]['server']!=companies[1]['server'],
                       dict(responses=companies,scope='sequential isolated networks; not overlapping bridges on one daemon'))
            self.report['status']='passed'

    def cleanup(self):
        if self.report.get('status') == 'failed':
            for name in self.containers:
                self.docker('exec', name, 'sh', '-c',
                            'ip addr; ip route; ip neigh; iptables -L -n -v; iptables -t nat -L -n -v', ok=False)
        for name in reversed(self.containers):
            p=self.docker('rm','-f',name,ok=False)
            self.report['cleanup'].append(dict(resource=name,returncode=p.returncode))
        for name in reversed(self.networks):
            p=self.docker('network','rm',name,ok=False)
            self.report['cleanup'].append(dict(resource=name,returncode=p.returncode))
        self.save()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--block',help='Optional unused private /22 for a transfer run')
    args=parser.parse_args()
    lab=Lab(args.output,args.block)
    try:
        lab.run()
    except BaseException as e:
        lab.report['status']='failed'
        lab.report['error']=str(e)
        raise
    finally:
        lab.cleanup()
    print(f"{len(lab.report['checks'])} checks passed; evidence: {args.output}")


if __name__ == '__main__':
    main()

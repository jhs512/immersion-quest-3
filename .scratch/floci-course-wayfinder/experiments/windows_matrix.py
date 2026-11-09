import json, time

def run(lab):
    A,I,S=lab.api,lab.inner,lab.save
    results=[]
    def record(name, value):
        results.append({'case':name,'observation':value}); S('matrix',results)
        print(name+': '+json.dumps(value,ensure_ascii=False)[:500],flush=True)
    def vpc(cidr): return A('create-vpc','--cidr-block',cidr)['Vpc']['VpcId']
    def subnet(v,cidr): return A('create-subnet','--vpc-id',v,'--cidr-block',cidr)['Subnet']['SubnetId']
    def sg(v): return A('create-security-group','--vpc-id',v,'--group-name','lab','--description','lab')['GroupId']
    def instance(s,g,ip=None):
        args=['--image-id','ami-alpine','--instance-type','t3.nano','--subnet-id',s,'--security-group-ids',g,'--no-associate-public-ip-address']
        if ip:args+=['--private-ip-address',ip]
        r=A('run-instances',*args)
        iid=r['Instances'][0]['InstanceId']
        def ready():
            x=A('describe-instances','--instance-ids',iid)['Reservations'][0]['Instances'][0]
            if x['State']['Name']=='terminated':raise RuntimeError('launch terminated: '+str(x))
            return x if x['State']['Name']=='running' else None
        x=lab.wait(ready,120)
        ids=I('ps','-aq').stdout.split()
        objects=json.loads(I('inspect',*ids).stdout)
        c=next(c for c in objects if 'AWS_EC2_INSTANCE_ID='+iid in c['Config']['Env'])
        cid=c['Id']; net=c['HostConfig']['NetworkMode']
        endpoint=json.loads(I('inspect',net.split(':',1)[1]).stdout)[0] if net.startswith('container:') else c
        addresses={k:z['IPAddress'] for k,z in endpoint['NetworkSettings']['Networks'].items()}
        S('instance-'+iid,{'api':x,'container':c,'endpoint':endpoint})
        record('instance-ready',{'id':iid,'container':cid,'private_ip':x['PrivateIpAddress'],'networks':addresses,'network_mode':net,'memory':c['HostConfig']['Memory'],'nano_cpus':c['HostConfig']['NanoCpus'],'port_bindings':c['HostConfig']['PortBindings']})
        I('exec',cid,'sh','-c',"printf 'HTTP/1.0 200 OK\\r\\nContent-Length: "+str(len(iid))+"\\r\\n\\r\\n"+iid+"' > /tmp/response")
        serve(cid)
        return {'id':iid,'container':cid,'ip':x['PrivateIpAddress'],'addresses':addresses}
    def serve(cid):
        I('exec','-d',cid,'sh','-c','while :; do nc -l -p 8080 -w 2 </tmp/response >/dev/null; done')
    def probe(src,dst,ip=None,port=8080):
        ip=ip or dst['ip']
        r=I('exec',src['container'],'wget','-T','2','-qO-',f'http://{ip}:{port}/',check=False)
        return {'src':src['id'],'dst':dst['id'],'ip':ip,'port':port,'rc':r.returncode,'body':r.stdout,'stderr':r.stderr,'marker_match':r.returncode==0 and r.stdout==dst['id']}
    def probes(name,a,b,c,d):
        record(name,[probe(a,b),probe(a,c),probe(a,d),probe(a,b,port=8081),probe(a,d,ip=d['addresses'].get('bridge'))])
        record(name+'-kernel-route',I('exec',a['container'],'ip','route').stdout)
    def terminate(xs):
        A('terminate-instances','--instance-ids',*[x['id'] for x in xs])
        for x in xs: lab.wait(lambda:I('inspect',x['container'],check=False).returncode!=0,90)
    def mode_default(cidr='10.91.0.0/16',second=False):
        prefix='10.91' if not second else '10.93'
        v=vpc(cidr);s1=subnet(v,prefix+'.1.0/24');s2=subnet(v,prefix+'.2.0/24');g=sg(v)
        if not second:
            record('vpc-subnet-query',{'vpcs':A('describe-vpcs','--vpc-ids',v),'subnets':A('describe-subnets','--filters',f'Name=vpc-id,Values={v}')})
            for name,action,args in [
                ('overlap-subnet','create-subnet',['--vpc-id',v,'--cidr-block',prefix+'.1.128/25']),
                ('outside-subnet','create-subnet',['--vpc-id',v,'--cidr-block','10.92.1.0/24']),
                ('too-small-subnet','create-subnet',['--vpc-id',v,'--cidr-block',prefix+'.3.0/29']),
                ('delete-vpc-dependency','delete-vpc',['--vpc-id',v]),
                ('reserved-ip','run-instances',['--image-id','ami-alpine','--instance-type','t3.nano','--subnet-id',s1,'--security-group-ids',g,'--private-ip-address',prefix+'.1.1']),
                ('outside-ip','run-instances',['--image-id','ami-alpine','--instance-type','t3.nano','--subnet-id',s1,'--security-group-ids',g,'--private-ip-address',prefix+'.9.10'])]:
                record(name,A(action,*args,check=False))
        a=instance(s1,g,prefix+'.1.10');b=instance(s1,g,prefix+'.1.11')
        record('same-subnet-second-cidr' if second else 'default-sg-empty-ingress',probe(a,b))
        if second:
            terminate([a,b]);A('delete-subnet','--subnet-id',s1);A('delete-subnet','--subnet-id',s2);A('delete-security-group','--group-id',g);record('selective-delete-second-vpc',A('delete-vpc','--vpc-id',v));return
        c=instance(s2,g,prefix+'.2.10');v2=vpc('10.92.0.0/16');s3=subnet(v2,'10.92.1.0/24');g2=sg(v2);d=instance(s3,g2,'10.92.1.10')
        probes('baseline-topology',a,b,c,d)
        record('default-bridge-bypass',[probe(a,d,ip=next(iter(d['addresses'].values())))])
        record('delete-live-subnet',A('delete-subnet','--subnet-id',s1,check=False))
        rt=A('create-route-table','--vpc-id',v)['RouteTable']['RouteTableId']
        A('associate-route-table','--route-table-id',rt,'--subnet-id',s1)
        igw=A('create-internet-gateway')['InternetGateway']['InternetGatewayId']
        A('attach-internet-gateway','--internet-gateway-id',igw,'--vpc-id',v)
        A('create-route','--route-table-id',rt,'--destination-cidr-block',prefix+'.2.0/24','--gateway-id',igw)
        record('igw-route-state',A('describe-route-tables','--route-table-ids',rt));probes('igw-route-packets',a,b,c,d)
        acl=A('create-network-acl','--vpc-id',v)['NetworkAcl']['NetworkAclId']
        for egress in [False,True]:
            A('create-network-acl-entry','--cli-input-json',json.dumps({'NetworkAclId':acl,'RuleNumber':1,'Protocol':'-1','RuleAction':'deny','CidrBlock':'0.0.0.0/0','Egress':egress}))
        acls=A('describe-network-acls','--filters',f'Name=vpc-id,Values={v}')['NetworkAcls']
        assoc=next(asc['NetworkAclAssociationId'] for n in acls for asc in n.get('Associations',[]) if asc['SubnetId']==s1)
        A('replace-network-acl-association','--association-id',assoc,'--network-acl-id',acl)
        record('deny-nacl-state',A('describe-network-acls','--network-acl-ids',acl));probes('deny-nacl-packets',a,b,c,d)
        peer=A('create-vpc-peering-connection','--vpc-id',v,'--peer-vpc-id',v2)['VpcPeeringConnection']['VpcPeeringConnectionId']
        A('accept-vpc-peering-connection','--vpc-peering-connection-id',peer)
        A('create-route','--route-table-id',rt,'--destination-cidr-block','10.92.0.0/16','--vpc-peering-connection-id',peer)
        record('peering-state',A('describe-vpc-peering-connections','--vpc-peering-connection-ids',peer));probes('peering-packets',a,b,c,d)
        allocation=A('allocate-address','--domain','vpc')['AllocationId']
        nat=A('create-nat-gateway','--subnet-id',s2,'--allocation-id',allocation)
        record('nat-create',nat)
        if 'NatGateway' in nat:
            nid=nat['NatGateway']['NatGatewayId'];A('create-route','--route-table-id',rt,'--destination-cidr-block','0.0.0.0/0','--nat-gateway-id',nid)
            record('nat-state',A('describe-nat-gateways','--nat-gateway-ids',nid));probes('nat-packets',a,b,c,d)
        A('stop-instances','--instance-ids',b['id'])
        lab.wait(lambda:not json.loads(I('inspect',b['container']).stdout)[0]['State']['Running'],90)
        record('stop-instance',{'api':A('describe-instances','--instance-ids',b['id']),'docker':json.loads(I('inspect',b['container']).stdout)[0]['State'],'probe':probe(a,b)})
        A('start-instances','--instance-ids',b['id']);lab.wait(lambda:json.loads(I('inspect',b['container']).stdout)[0]['State']['Running']);time.sleep(2)
        serve(b['container'])
        record('restart-instance-packets',probe(a,b))
        terminate([a,b,c,d]);record('terminated-state',A('describe-instances','--instance-ids',a['id'],b['id']))
        mode_default('10.93.0.0/16',True)
    mode_default()
    I('logs','floci',label='default-mode-log')
    I('stop','floci');I('rm','floci')
    lab.start_floci(True)
    v=vpc('10.94.0.0/16');s=subnet(v,'10.94.1.0/24');ga=sg(v)
    gb=A('create-security-group','--vpc-id',v,'--group-name','target','--description','target')['GroupId']
    try:
        a=instance(s,ga,'10.94.1.10');b=instance(s,gb,'10.94.1.11')
        # The protected namespace uses a transport address. Test both logical and real addresses.
        ip=next(iter(b['addresses'].values()))
        record('sg-enforced-default-deny',{'logical':probe(a,b),'transport':probe(a,b,ip=ip)})
        perm=json.dumps([{'IpProtocol':'tcp','FromPort':8080,'ToPort':8080,'IpRanges':[{'CidrIp':'0.0.0.0/0'}]}])
        A('authorize-security-group-ingress','--group-id',gb,'--ip-permissions',perm);time.sleep(2)
        record('sg-ingress-allow',{'logical':probe(a,b),'transport':probe(a,b,ip=ip)})
        A('revoke-security-group-ingress','--group-id',gb,'--ip-permissions',perm);time.sleep(2)
        record('sg-ingress-revoke',probe(a,b,ip=ip))
        A('authorize-security-group-ingress','--group-id',gb,'--ip-permissions',perm);time.sleep(2)
        record('sg-ingress-restore',probe(a,b,ip=ip))
        allout=json.dumps([{'IpProtocol':'-1','IpRanges':[{'CidrIp':'0.0.0.0/0'}]}])
        A('revoke-security-group-egress','--group-id',ga,'--ip-permissions',allout);time.sleep(2)
        record('sg-egress-deny',probe(a,b,ip=ip))
        A('authorize-security-group-egress','--group-id',ga,'--ip-permissions',perm);time.sleep(2)
        record('sg-egress-allow',probe(a,b,ip=ip))
        A('revoke-security-group-egress','--group-id',ga,'--ip-permissions',perm);time.sleep(2)
        record('sg-egress-revoke',probe(a,b,ip=ip))
        A('authorize-security-group-egress','--group-id',ga,'--ip-permissions',allout);time.sleep(2)
        record('sg-egress-restore',probe(a,b,ip=ip))
        terminate([a,b])
    except Exception as e:
        record('sg-runtime-limit',repr(e))
    S('inner-networks',json.loads(I('network','inspect',*I('network','ls','-q').stdout.split()).stdout))
    record('outer-port-verification',json.loads(lab.docker('inspect',lab.RUN).stdout)[0]['HostConfig']['PortBindings'])

"""Focused clean peering delta: default NACLs, both subnet route tables."""
import json, time, traceback
import windows_lab as L

R=[]
def rec(name,value):
    R.append({'case':name,'observation':value});L.save('peering-matrix',R)
    print(name+': '+json.dumps(value)[:600],flush=True)

def launch(cidr,ip):
    v=L.api('create-vpc','--cidr-block',cidr)['Vpc']['VpcId']
    s=L.api('create-subnet','--vpc-id',v,'--cidr-block',ip.rsplit('.',1)[0]+'.0/24')['Subnet']['SubnetId']
    g=L.api('create-security-group','--vpc-id',v,'--group-name','lab','--description','lab')['GroupId']
    iid=L.api('run-instances','--image-id','ami-alpine','--instance-type','t3.nano','--subnet-id',s,'--security-group-ids',g,'--private-ip-address',ip,'--no-associate-public-ip-address')['Instances'][0]['InstanceId']
    def ready():
        o=L.api('describe-instances','--instance-ids',iid)['Reservations'][0]['Instances'][0]
        return o if o['State']['Name']=='running' else None
    api=L.wait(ready,120)
    objects=json.loads(L.inner('inspect',*L.inner('ps','-aq').stdout.split()).stdout)
    c=next(o for o in objects if 'AWS_EC2_INSTANCE_ID='+iid in o['Config']['Env'])
    L.save(iid,{'api':api,'container':c})
    L.inner('exec',c['Id'],'sh','-c',"printf 'HTTP/1.0 200 OK\\r\\nContent-Length: "+str(len(iid))+"\\r\\n\\r\\n"+iid+"' >/tmp/response")
    L.inner('exec','-d',c['Id'],'sh','-c','while :; do nc -l -p 8080 -w 2 </tmp/response >/dev/null; done')
    rt=L.api('create-route-table','--vpc-id',v)['RouteTable']['RouteTableId']
    L.api('associate-route-table','--route-table-id',rt,'--subnet-id',s)
    return {'vpc':v,'subnet':s,'sg':g,'id':iid,'container':c['Id'],'ip':ip,'cidr':cidr,'rt':rt,'bridge':c['NetworkSettings']['Networks']['bridge']['IPAddress']}

def probe(a,b,ip=None,port=8080):
    r=L.inner('exec',a['container'],'wget','-T','2','-qO-',f"http://{ip or b['ip']}:{port}/",check=False)
    return {'src':a['id'],'dst':b['id'],'ip':ip or b['ip'],'port':port,'rc':r.returncode,'body':r.stdout,'marker_match':r.returncode==0 and r.stdout==b['id'],'stderr':r.stderr}

def snapshot(name,a,b):
    rec(name,{'forward':probe(a,b),'reverse':probe(b,a),'bridge_control':probe(a,b,b['bridge']),'closed_port':probe(a,b,b['bridge'],8081),'routes_a':L.inner('exec',a['container'],'ip','route').stdout,'routes_b':L.inner('exec',b['container'],'ip','route').stdout})

if __name__=='__main__':
    print(L.OUT,flush=True)
    failed=False
    try:
        L.bootstrap();L.start_floci()
        a=launch('10.95.0.0/16','10.95.1.10');b=launch('10.96.0.0/16','10.96.1.10')
        rec('topology',[a,b]);snapshot('before-peering',a,b)
        peer=L.api('create-vpc-peering-connection','--vpc-id',a['vpc'],'--peer-vpc-id',b['vpc'])['VpcPeeringConnection']['VpcPeeringConnectionId']
        L.api('accept-vpc-peering-connection','--vpc-peering-connection-id',peer)
        for src,dst in [(a,b),(b,a)]:
            L.api('create-route','--route-table-id',src['rt'],'--destination-cidr-block',dst['cidr'],'--vpc-peering-connection-id',peer)
        rec('peer-state',L.api('describe-vpc-peering-connections','--vpc-peering-connection-ids',peer))
        rec('route-state',L.api('describe-route-tables','--route-table-ids',a['rt'],b['rt']))
        rec('default-nacls',L.api('describe-network-acls','--filters',f"Name=vpc-id,Values={a['vpc']},{b['vpc']}"))
        snapshot('after-bidirectional-peering',a,b)
        L.api('delete-vpc-peering-connection','--vpc-peering-connection-id',peer)
        snapshot('after-peering-delete',a,b)
        L.api('terminate-instances','--instance-ids',a['id'],b['id'])
        for x in [a,b]:L.wait(lambda:L.inner('inspect',x['container'],check=False).returncode!=0)
    except BaseException:
        failed=True;L.save('fatal',{'traceback':traceback.format_exc()});print(traceback.format_exc(),flush=True)
    finally:L.cleanup();print('CLEANED',flush=True)
    if failed:raise SystemExit(1)

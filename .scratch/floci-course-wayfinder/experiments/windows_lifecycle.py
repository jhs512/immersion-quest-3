"""Lifecycle supplement: poll real stopped state instead of assuming fixed sleep."""
import json, traceback
from windows_peering import L, launch, probe

RESULTS=[]
def rec(name,value):
    RESULTS.append({'case':name,'observation':value});L.save('lifecycle-matrix',RESULTS)
    print(name+': '+json.dumps(value)[:600],flush=True)

if __name__=='__main__':
    print(L.OUT,flush=True)
    failed=False
    try:
        L.bootstrap();L.start_floci()
        a=launch('10.97.0.0/16','10.97.1.10');b=launch('10.98.0.0/16','10.98.1.10')
        rec('lifecycle-baseline',probe(a,b,b['bridge']))
        L.api('stop-instances','--instance-ids',b['id'])
        L.wait(lambda:not json.loads(L.inner('inspect',b['container']).stdout)[0]['State']['Running'],90)
        L.wait(lambda:L.api('describe-instances','--instance-ids',b['id'])['Reservations'][0]['Instances'][0]['State']['Name']=='stopped',90)
        rec('stopped-confirmed',{'api':L.api('describe-instances','--instance-ids',b['id']),'docker':json.loads(L.inner('inspect',b['container']).stdout)[0]['State'],'probe':probe(a,b,b['bridge'])})
        L.api('start-instances','--instance-ids',b['id'])
        L.wait(lambda:L.api('describe-instances','--instance-ids',b['id'])['Reservations'][0]['Instances'][0]['State']['Name']=='running',90)
        c=json.loads(L.inner('inspect',b['container']).stdout)[0]
        b['bridge']=c['NetworkSettings']['Networks']['bridge']['IPAddress']
        L.inner('exec','-d',b['container'],'sh','-c','while :; do nc -l -p 8080 -w 2 </tmp/response >/dev/null; done')
        rec('started-confirmed',{'docker':c['State'],'probe':probe(a,b,b['bridge'])})
        L.api('terminate-instances','--instance-ids',a['id'],b['id'])
        for x in [a,b]:L.wait(lambda:L.inner('inspect',x['container'],check=False).returncode!=0,90)
        rec('terminated-confirmed',{'api':L.api('describe-instances','--instance-ids',a['id'],b['id']),'containers_removed':True})
    except BaseException:
        failed=True;L.save('fatal',{'traceback':traceback.format_exc()});print(traceback.format_exc(),flush=True)
    finally:L.cleanup();print('CLEANED',flush=True)
    if failed:raise SystemExit(1)

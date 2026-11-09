"""Disposable actual database experiment. Run only after coordinator runtime GO.
Host AWS commands always use loopback and dummy credentials. No host socket mounts.
"""
import pathlib, datetime, json, subprocess, os, time, traceback, tempfile, sys

ROOT=pathlib.Path(__file__).resolve().parent
RUN='mq-floci-db-'+datetime.datetime.now().strftime('%Y%m%d%H%M%S')
OUT=ROOT/RUN
EVENTS=[]
PORT='45671'
DIND='docker@sha256:ecac43e78380d9b9d3bd24f0ab42b370f6391a1a06a66065c10a00b9d6d57a3e'
FLOCI='floci/floci@sha256:5ee85db604c4aa74ac76e07ea5cc83086f37bb472bf3dbb97e34019e48efae9c'
PG='postgres:16-alpine'
AWS=r'C:\Program Files\Amazon\AWSCLIV2\aws.exe'
ENV={k:v for k,v in os.environ.items() if not k.startswith('AWS_')}

def save(n,o): (OUT/(n+'.json')).write_text(json.dumps(o,ensure_ascii=False,indent=2),encoding='utf8')
def cmd(a,check=True,timeout=120,label=None):
    t=time.time();r=subprocess.run(a,env=ENV,capture_output=True,text=True,encoding='utf8',errors='replace',timeout=timeout)
    EVENTS.append(dict(label=label,argv=a,rc=r.returncode,seconds=round(time.time()-t,3),stdout=r.stdout,stderr=r.stderr));save('events',EVENTS)
    if check and r.returncode: raise RuntimeError(str(a[:4])+': '+r.stderr[-900:])
    return r
def docker(*a,**kw): return cmd(['docker',*a],**kw)
def inner(*a,**kw): return docker('exec',RUN,'docker',*a,**kw)
def api(service,action,payload=None,check=True):
    args=[AWS,'--endpoint-url','http://127.0.0.1:'+PORT,'--region','us-east-1','--output','json','--cli-connect-timeout','3','--cli-read-timeout','120',service,action]
    if payload is not None:
        p=OUT/('request-'+str(len(EVENTS))+'.json');p.write_text(json.dumps(payload),encoding='utf8');args+=['--cli-input-json','file://'+str(p)]
    r=cmd(args,check=check,timeout=150,label=service+'.'+action)
    return json.loads(r.stdout) if r.returncode==0 and r.stdout.strip() else {'rc':r.returncode,'error':r.stderr}
def wait(fn,seconds=180):
    until=time.time()+seconds
    while time.time()<until:
        try:
            r=fn()
            if r:return r
        except Exception:pass
        time.sleep(2)
    raise TimeoutError('readiness timeout')
def inventory():
    return {'containers':docker('ps','-aq','--no-trunc').stdout.split(),'networks':sorted(docker('network','ls','--format','{{json .}}').stdout.splitlines()),'volumes':sorted(docker('volume','ls','--format','{{json .}}').stdout.splitlines())}
def transfer(image):
    before=json.loads(docker('image','inspect',image).stdout)[0];save('host-image-'+('floci' if image==FLOCI else 'postgres'),before)
    tar=pathlib.Path(tempfile.gettempdir())/(RUN+('-floci.tar' if image==FLOCI else '-pg.tar'))
    try:
        docker('save','-o',str(tar),image,timeout=180)
        docker('cp',str(tar),RUN+':/tmp/image.tar',timeout=180)
        loaded=inner('load','-i','/tmp/image.tar',timeout=180)
        # Docker save of a digest-only reference retains the image ID, not always its repo digest.
        reference=loaded.stdout.strip().splitlines()[-1].split(': ',1)[1]
        inner('tag',reference, 'mq-floci-pinned:2.4.0' if image==FLOCI else PG)
        after=json.loads(inner('image','inspect',reference).stdout)[0]
        # Desktop containerd reports an OCI index ID; classic DIND reports config ID.
        assert after['RootFS']==before['RootFS'] and after['Architecture']==before['Architecture']
        save('image-transfer-'+('floci' if image==FLOCI else 'postgres'),{'hostIndex':before['Id'],'innerConfig':after['Id'],'rootfsMatch':True,'loadedReference':reference})
        docker('exec',RUN,'rm','/tmp/image.tar')
    finally:
        if tar.exists():tar.unlink()
def start_floci():
    inner('run','-d','--name','floci','--label','mq.lab='+RUN,'--cpus','2','--memory','2g','--memory-swap','2g','--pids-limit','512','--network','host','-v','/var/run/docker.sock:/var/run/docker.sock','-e','FLOCI_DOCKER_RESOURCE_NAMESPACE='+RUN,'-e','FLOCI_STORAGE_MODE=memory','-e','FLOCI_SERVICES_RDS_DEFAULT_POSTGRES_IMAGE='+PG,'mq-floci-pinned:2.4.0')
    wait(lambda:'TableNames' in api('dynamodb','list-tables',check=False))
def ddb():
    def call(a,p=None,check=True):return api('dynamodb',a,p,check)
    schema=dict(AttributeDefinitions=[{'AttributeName':'pk','AttributeType':'S'},{'AttributeName':'sk','AttributeType':'N'}],KeySchema=[{'AttributeName':'pk','KeyType':'HASH'},{'AttributeName':'sk','KeyType':'RANGE'}],BillingMode='PAY_PER_REQUEST')
    def key(pk='A',sk=1):return {'pk':{'S':pk},'sk':{'N':str(sk)}}
    def get(pk='A',sk=1,table='books'):return call('get-item',dict(TableName=table,Key=key(pk,sk),ConsistentRead=True)).get('Item')
    for table in ['books','sibling']:
        call('create-table',dict(TableName=table,**schema));wait(lambda:call('describe-table',{'TableName':table})['Table']['TableStatus']=='ACTIVE')
    for pk,sk,v in [('A',1,10),('A',2,20),('B',1,30)]:call('put-item',dict(TableName='books',Item=dict(**key(pk,sk),qty={'N':str(v)})))
    assert get()['qty']=={'N':'10'}
    for bad in [{'pk':{'N':'1'},'sk':{'N':'1'}},{'pk':{'S':'A'}}]:
        assert call('get-item',dict(TableName='books',Key=bad),False).get('rc',0)!=0
    q=call('query',dict(TableName='books',KeyConditionExpression='pk = :p AND sk >= :s',ExpressionAttributeValues={':p':{'S':'A'},':s':{'N':'2'}}));assert q['Count']==1
    s=call('scan',dict(TableName='books',FilterExpression='qty >= :q',ExpressionAttributeValues={':q':{'N':'20'}}));assert s['Count']==2 and s['ScannedCount']==3
    assert call('query',dict(TableName='books',KeyConditionExpression='sk = :s',ExpressionAttributeValues={':s':{'N':'1'}}),False).get('rc',0)!=0
    call('update-item',dict(TableName='books',Key=key(),UpdateExpression='SET qty = :q',ConditionExpression='qty = :old',ExpressionAttributeValues={':q':{'N':'11'},':old':{'N':'10'}}));assert get()['qty']=={'N':'11'}
    assert call('put-item',dict(TableName='books',Item=dict(**key(),qty={'N':'999'}),ConditionExpression='attribute_not_exists(pk)'),False).get('rc',0)!=0
    assert get()['qty']=={'N':'11'}
    def tx(value,condition):return {'TransactItems':[{'Put':{'TableName':'books','Item':dict(**key('T',1),qty={'N':str(value)})}},{'ConditionCheck':{'TableName':'books','Key':key(),'ConditionExpression':'qty = :q','ExpressionAttributeValues':{':q':{'N':str(condition)}}}}]}
    ok=call('transact-write-items',tx(40,11),False);save('ddb-transaction-success',ok)
    if not ok.get('rc'):
        assert get('T')['qty']=={'N':'40'}
        bad=call('transact-write-items',tx(99,999),False);assert bad.get('rc',0)!=0;assert get('T')['qty']=={'N':'40'}
    call('delete-item',dict(TableName='books',Key=key('A',2)));assert get('A',2) is None
    call('put-item',dict(TableName='sibling',Item=dict(**key(),qty={'N':'77'})))
    call('delete-table',{'TableName':'books'});assert get(table='sibling')['qty']=={'N':'77'}
    assert call('describe-table',{'TableName':'books'},False).get('rc',0)!=0
    call('create-table',dict(TableName='books',**schema));assert get() is None
    save('ddb-summary',{'crud':True,'key-negatives':True,'query-scan':True,'conditions':True,'transaction-supported':not bool(ok.get('rc')),'selective-delete-recreate':True})

def rds():
    def call(a,p=None,check=True):return api('rds',a,p,check)
    base=dict(DBInstanceClass='db.t3.micro',Engine='postgres',EngineVersion='16',MasterUsername='labuser',MasterUserPassword='fake-lab-password-42',AllocatedStorage=5,DBName='labdb')
    call('create-db-instance',dict(DBInstanceIdentifier='labpg',**base))
    wait(lambda:call('describe-db-instances',{'DBInstanceIdentifier':'labpg'})['DBInstances'][0]['DBInstanceStatus']=='available')
    def find():
        ids=inner('ps','-aq','--filter','label=floci.service=rds').stdout.split()
        if not ids:ids=[x for x in inner('ps','-a','--format','{{.Names}}').stdout.split() if 'rds' in x]
        assert len(ids)==1,ids
        return ids[0]
    def sql(query,check=True,proxy=False):
        args=['exec',cid,'psql','-X','-v','ON_ERROR_STOP=1','-U','labuser','-d','labdb','-At']
        if proxy:
            ep=call('describe-db-instances',{'DBInstanceIdentifier':'labpg'})['DBInstances'][0]['Endpoint']
            # Floci uses inner host network. Its proxy is reached through the DB bridge gateway;
            # advertised loopback would point at the client container itself.
            info=json.loads(inner('inspect',cid).stdout)[0]
            gateway=next(v['Gateway'] for v in info['NetworkSettings']['Networks'].values() if v.get('Gateway'))
            save('rds-proxy-client-route',{'advertised':ep,'clientHost':gateway,'reason':'inner DIND host-network proxy from DB bridge'})
            args=['exec','-e','PGPASSWORD=fake-lab-password-42',cid,'psql','-X','-v','ON_ERROR_STOP=1','-h',gateway,'-p',str(ep['Port']),'-U','labuser','-d','labdb','-At']
        return inner(*args,'-c',query,check=check,label='sql-proxy' if proxy else 'sql')
    cid=find()
    inner('update','--cpus','1','--memory','512m','--memory-swap','512m','--pids-limit','256',cid)
    save('rds-cgroup-before',{'limits':inner('exec',cid,'cat','/sys/fs/cgroup/memory.max','/sys/fs/cgroup/cpu.max','/sys/fs/cgroup/pids.max').stdout,'processes':inner('top',cid).stdout})
    wait(lambda:sql('SELECT 1',False).returncode==0)
    save('rds-process-before',json.loads(inner('inspect',cid).stdout));save('rds-image',json.loads(inner('image','inspect',PG).stdout))
    sql('SELECT version();');proxy=sql('SELECT system_identifier FROM pg_control_system()',False,True);save('rds-proxy-result',{'rc':proxy.returncode,'stdout':proxy.stdout,'stderr':proxy.stderr})
    if proxy.returncode==0:assert proxy.stdout==sql('SELECT system_identifier FROM pg_control_system()').stdout
    sql('CREATE TABLE stock(id integer PRIMARY KEY, qty integer CHECK(qty>=0)); INSERT INTO stock VALUES(1,10); SELECT * FROM stock;')
    assert sql('SELECT qty FROM stock WHERE id=1').stdout.strip()=='10'
    if proxy.returncode==0:assert sql('SELECT qty FROM stock WHERE id=1',proxy=True).stdout.strip()=='10'
    assert sql('INSERT INTO stock VALUES(1,999)',False).returncode!=0
    assert sql('UPDATE stock SET qty=-1 WHERE id=1',False).returncode!=0
    assert sql('SELECT qty FROM stock WHERE id=1').stdout.strip()=='10'
    sql('BEGIN; UPDATE stock SET qty=20 WHERE id=1; ROLLBACK;');assert sql('SELECT qty FROM stock WHERE id=1').stdout.strip()=='10'
    sql('BEGIN; UPDATE stock SET qty=30 WHERE id=1; COMMIT;');assert sql('SELECT qty FROM stock WHERE id=1').stdout.strip()=='30'
    sql('INSERT INTO stock VALUES(2,5); DELETE FROM stock WHERE id=2;');assert sql('SELECT count(*) FROM stock').stdout.strip()=='1'
    snap=call('create-db-snapshot',{'DBInstanceIdentifier':'labpg','DBSnapshotIdentifier':'lab-snapshot'},False);save('rds-snapshot-result',snap)
    sql('INSERT INTO stock VALUES(3,55)')
    call('stop-db-instance',{'DBInstanceIdentifier':'labpg'});wait(lambda:call('describe-db-instances',{'DBInstanceIdentifier':'labpg'})['DBInstances'][0]['DBInstanceStatus']=='stopped')
    save('rds-stopped-containers',inner('ps','-a','--format','{{json .}}').stdout.splitlines())
    assert sql('SELECT 1',False).returncode!=0
    call('start-db-instance',{'DBInstanceIdentifier':'labpg'});wait(lambda:call('describe-db-instances',{'DBInstanceIdentifier':'labpg'})['DBInstances'][0]['DBInstanceStatus']=='available')
    cid=find();inner('update','--cpus','1','--memory','512m','--memory-swap','512m','--pids-limit','256',cid);wait(lambda:sql('SELECT 1',False).returncode==0)
    save('rds-cgroup-restarted',{'limits':inner('exec',cid,'cat','/sys/fs/cgroup/memory.max','/sys/fs/cgroup/cpu.max','/sys/fs/cgroup/pids.max').stdout,'processes':inner('top',cid).stdout})
    assert sql('SELECT qty FROM stock WHERE id=1').stdout.strip()=='30';save('rds-process-restarted',json.loads(inner('inspect',cid).stdout))
    restore_ok=False
    if not snap.get('rc'):
        restore=call('restore-db-instance-from-db-snapshot',{'DBInstanceIdentifier':'restoredpg','DBSnapshotIdentifier':'lab-snapshot','DBInstanceClass':'db.t3.micro'},False);save('rds-restore-result',restore)
        if not restore.get('rc'):
            wait(lambda:call('describe-db-instances',{'DBInstanceIdentifier':'restoredpg'})['DBInstances'][0]['DBInstanceStatus']=='available')
            original=json.loads(inner('inspect',cid).stdout)[0]['Name'].lstrip('/')
            names=inner('ps','--format','{{.Names}}').stdout.split();cid=next(x for x in names if 'rds' in x and x!=original)
            inner('update','--cpus','1','--memory','512m','--memory-swap','512m','--pids-limit','256',cid);wait(lambda:sql('SELECT 1',False).returncode==0)
            assert sql('SELECT qty FROM stock WHERE id=1').stdout.strip()=='30';assert sql('SELECT count(*) FROM stock WHERE id=3').stdout.strip()=='0'
            restore_ok=True
            call('delete-db-instance',{'DBInstanceIdentifier':'labpg','SkipFinalSnapshot':True});assert sql('SELECT qty FROM stock WHERE id=1').stdout.strip()=='30'
            call('delete-db-instance',{'DBInstanceIdentifier':'restoredpg','SkipFinalSnapshot':True});call('delete-db-snapshot',{'DBSnapshotIdentifier':'lab-snapshot'})
    if not restore_ok:call('delete-db-instance',{'DBInstanceIdentifier':'labpg','SkipFinalSnapshot':True})
    wait(lambda:call('describe-db-instances',{'DBInstanceIdentifier':'labpg'},False).get('rc',0)!=0)
    save('rds-summary',{'real-sql-crud':True,'constraints':True,'transactions':True,'stop-start-persistence':True,'snapshot-restored-sql':restore_ok,'proxy-sql':proxy.returncode==0})

def cleanup():
    if docker('inspect',RUN,check=False).returncode==0:
        save('inner-final-inventory',inner('ps','-a','--format','{{json .}}',check=False).stdout.splitlines());inner('logs','floci',check=False)
        assert json.loads(docker('inspect',RUN).stdout)[0]['Config']['Labels']['mq.lab']==RUN
        docker('rm','-f',RUN)
    for kind in ['volume','network']:
        r=docker(kind,'inspect',RUN,check=False)
        if r.returncode==0:
            assert json.loads(r.stdout)[0]['Labels']['mq.lab']==RUN;docker(kind,'rm',RUN)
    after=inventory();save('host-after',after);assert after==json.loads((OUT/'host-before.json').read_text())

if __name__=='__main__':
    assert os.environ.get('MQ_FLOCI_RUNTIME_GO')=='yes','coordinator runtime gate required'
    OUT.mkdir();empty=OUT/'empty-aws-config';empty.write_text('')
    ENV.update(AWS_ACCESS_KEY_ID='test',AWS_SECRET_ACCESS_KEY='test',AWS_DEFAULT_REGION='us-east-1',AWS_CONFIG_FILE=str(empty),AWS_SHARED_CREDENTIALS_FILE=str(empty),AWS_EC2_METADATA_DISABLED='true',AWS_PAGER='')
    print(str(OUT),flush=True)
    failed=False
    try:
        save('host-before',inventory());save('docker-version',json.loads(docker('version','--format','{{json .}}').stdout))
        docker('network','create','--label','mq.lab='+RUN,RUN);docker('volume','create','--label','mq.lab='+RUN,RUN)
        docker('run','-d','--name',RUN,'--label','mq.lab='+RUN,'--privileged','--cgroupns=host','--cpus','4','--memory','6g','--memory-swap','6g','--pids-limit','2048','--network',RUN,'-p','127.0.0.1:'+PORT+':4566','-v',RUN+':/var/lib/docker','--entrypoint','dockerd',DIND,'--host=unix:///var/run/docker.sock','--storage-driver=overlay2')
        wait(lambda:inner('info',check=False).returncode==0);save('outer-inspect',json.loads(docker('inspect',RUN).stdout))
        transfer(FLOCI);transfer(PG);start_floci()
        matrix=[('rds',rds)] if '--only-rds' in sys.argv else [('dynamodb',ddb),('rds',rds)]
        for label,fn in matrix:
            try:fn();print(label+' finished',flush=True)
            except Exception:failed=True;save(label+'-failure',{'traceback':traceback.format_exc()});print(traceback.format_exc(),flush=True)
        inner('restart','floci');wait(lambda:'TableNames' in api('dynamodb','list-tables',check=False));save('ddb-memory-restart',api('dynamodb','list-tables'))
    except BaseException:failed=True;save('fatal',{'traceback':traceback.format_exc()});print(traceback.format_exc(),flush=True)
    finally:cleanup();print('CLEANED',flush=True)
    if failed:raise SystemExit(1)

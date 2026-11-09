"""Bounded persistence and replay supplement. Separate from original 23 checks."""
import json,zipfile,time,hashlib

def run(h):
    checks=[]
    def check(name,condition,detail=None):
        checks.append({'name':name,'passed':bool(condition),'detail':detail});h.save('checks',checks);print(name,bool(condition),flush=True)
    def api(service,action,*args,ok=True):
        r=h.cmd([h.AWS,'--endpoint-url',f'http://127.0.0.1:{h.PORT}','--region','us-east-1','--output','json','--cli-binary-format','raw-in-base64-out','--cli-connect-timeout','5','--cli-read-timeout','45',service,action,*map(str,args)],check=ok,label=service+':'+action)
        return json.loads(r.stdout) if r.returncode==0 and r.stdout.strip() else {'rc':r.returncode,'error':r.stderr}
    def put(key,data):
        f=h.OUT/'put.bin';f.write_bytes(data);return api('s3api','put-object','--bucket','mq-supplement','--key',key,'--body',f)
    def get(key):
        f=h.OUT/'get.bin';r=api('s3api','get-object','--bucket','mq-supplement','--key',key,f,ok=False)
        return None if 'rc' in r else f.read_bytes()
    # Replace empty memory service with explicitly configured persistent S3 volume.
    h.inner('rm','-f','floci')
    h.inner('volume','create','--label',f'mq.lab={h.RUN}','mq-s3-persistent')
    h.inner('run','-d','--name','floci','--label',f'mq.lab={h.RUN}','--cpus','2','--memory','2g','--pids-limit','512','--network','host','-v','/var/run/docker.sock:/var/run/docker.sock','-v','mq-s3-persistent:/app/data','-e',f'FLOCI_DOCKER_RESOURCE_NAMESPACE={h.RUN}','-e','FLOCI_STORAGE_MODE=memory','-e','FLOCI_STORAGE_SERVICES_S3_MODE=persistent','-e','FLOCI_STORAGE_PERSISTENT_PATH=/app/data','-e','FLOCI_SERVICES_LAMBDA_DOCKER_HOST_OVERRIDE=172.17.0.1',h.FLOCI)
    h.wait(lambda:api('s3api','list-buckets',ok=False).get('Buckets') is not None)
    api('s3api','create-bucket','--bucket','mq-supplement')
    data=bytes(range(256))+'\n지속 저장'.encode();put('persistent/한글.bin',data)
    check('persistent-before-restart-exact-bytes',get('persistent/한글.bin')==data)
    h.save('persistent-config-inspect',json.loads(h.inner('inspect','floci').stdout))
    h.inner('restart','--timeout','20','floci');h.wait(lambda:api('s3api','list-buckets',ok=False).get('Buckets') is not None)
    actual=get('persistent/한글.bin')
    check('persistent-process-restart-exact-bytes',actual==data,{'length':len(data),'expected_sha256':hashlib.sha256(data).hexdigest(),'actual_sha256':hashlib.sha256(actual).hexdigest() if actual is not None else None})
    # Real Lambda handler, explicit SDK target, deterministic overwrite by event key.
    runtime='public.ecr.aws/lambda/python@sha256:238f6bfd2c1c188aff3955c2f7ceb767fe9da1b3597d84264426a11690fcf2d7'
    h.inner('pull',runtime,timeout=300);h.inner('tag',runtime,'public.ecr.aws/lambda/python:3.12')
    h.save('lambda-runtime-image',json.loads(h.inner('image','inspect',runtime).stdout))
    code='''import boto3,urllib.parse
from botocore.config import Config
def handler(event,context):
 s=boto3.client('s3',endpoint_url='http://172.17.0.1:4566',aws_access_key_id='test',aws_secret_access_key='test',region_name='us-east-1',config=Config(s3={'addressing_style':'path'},connect_timeout=2,read_timeout=3,retries={'max_attempts':0}))
 for r in event['Records']:
  b=r['s3']['bucket']['name'];k=urllib.parse.unquote_plus(r['s3']['object']['key'])
  data=s.get_object(Bucket=b,Key=k)['Body'].read()
  s.put_object(Bucket=b,Key='processed/'+k[len('incoming/'):],Body=b'PROCESSED:'+data.upper())
 return {'records':len(event['Records'])}
'''
    z=h.OUT/'function.zip'
    with zipfile.ZipFile(z,'w') as f:f.writestr('main.py',code)
    api('lambda','create-function','--function-name','mq-replay','--runtime','python3.12','--handler','main.handler','--role','arn:aws:iam::000000000000:role/test','--timeout','5','--memory-size','128','--zip-file','fileb://'+str(z))
    put('incoming/한글 input.txt',b'replay source')
    event={'Records':[{'eventName':'ObjectCreated:Put','s3':{'bucket':{'name':'mq-supplement'},'object':{'key':'incoming/%ED%95%9C%EA%B8%80+input.txt'}}}]}
    outputs=[];keysets=[];invokes=[]
    for n in range(2):
        f=h.OUT/f'replay-response-{n+1}.json';r=api('lambda','invoke','--function-name','mq-replay','--payload',json.dumps(event),f)
        invokes.append({'metadata':r,'body':json.loads(f.read_text())});outputs.append(get('processed/한글 input.txt'))
        keysets.append([x['Key'] for x in api('s3api','list-objects-v2','--bucket','mq-supplement','--prefix','processed/').get('Contents',[])])
    check('same-event-replayed-twice-handler-success',all(x['metadata'].get('StatusCode')==200 and not x['metadata'].get('FunctionError') and x['body']=={'records':1} for x in invokes),invokes)
    check('same-event-deterministic-output',outputs==[b'PROCESSED:REPLAY SOURCE']*2,[repr(x) for x in outputs])
    # CLI stdout encoding can render non-ASCII keys differently on Windows.
    # Exact-key GET above proves identity; count one proves absence of extras.
    check('same-event-no-extra-output-keys',all(len(keys)==1 for keys in keysets) and outputs==[b'PROCESSED:REPLAY SOURCE']*2,keysets)
    inspect=json.loads(h.inner('inspect',*h.inner('ps','-aq').stdout.split()).stdout);h.save('inner-service-inspect',inspect)
    check('nested-no-published-ports',all(not x['HostConfig'].get('PortBindings') for x in inspect))
    h.save('summary',{'checks':len(checks),'passed':sum(x['passed'] for x in checks),'failed':[x['name'] for x in checks if not x['passed']]})

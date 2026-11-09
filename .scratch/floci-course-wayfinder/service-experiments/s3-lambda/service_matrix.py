"""Small bounded assertions against only lab's explicit loopback endpoint."""
import json, zipfile, hashlib, time

def run(h):
    checks=[]
    def check(name, condition, detail=None):
        checks.append(dict(name=name,passed=bool(condition),detail=detail)); h.save('checks',checks)
        print(name, bool(condition),flush=True)
    def api(service,action,*args,ok=True):
        r=h.cmd([h.AWS,'--endpoint-url',f'http://127.0.0.1:{h.PORT}','--region','us-east-1','--output','json','--cli-binary-format','raw-in-base64-out','--cli-connect-timeout','5','--cli-read-timeout','45',service,action,*map(str,args)],check=ok,label=service+':'+action)
        return json.loads(r.stdout) if r.returncode==0 and r.stdout.strip() else {'rc':r.returncode,'error':r.stderr}
    def put(bucket,key,data):
        f=h.OUT/'put.bin';f.write_bytes(data);return api('s3api','put-object','--bucket',bucket,'--key',key,'--body',f)
    def get(bucket,key,ok=True):
        f=h.OUT/'get.bin';r=api('s3api','get-object','--bucket',bucket,'--key',key,f,ok=ok)
        return r, f.read_bytes() if 'rc' not in r else None
    b='mq-s3lambda'; api('s3api','create-bucket','--bucket',b)
    check('bucket-create-query',b in [x['Name'] for x in api('s3api','list-buckets')['Buckets']])
    for key,data in [('raw/binary',bytes(range(256))),('raw/한글 공백.txt','안녕\n世界'.encode()),('raw/empty',b'')]:
        put(b,key,data);r,actual=get(b,key);check('bytes-'+key,actual==data,{'length':len(data),'sha256':hashlib.sha256(actual).hexdigest()})
    check('missing-key','NoSuchKey' in get(b,'absent',False)[0].get('error',''))
    check('missing-bucket','NoSuchBucket' in get('mq-absent-bucket','absent',False)[0].get('error',''))
    put(b,'raw/binary',b'changed');check('overwrite',get(b,'raw/binary')[1]==b'changed')
    keys=[x['Key'] for x in api('s3api','list-objects-v2','--bucket',b,'--prefix','raw/')['Contents']]
    check('prefix-distinct-keys',len(keys)==3,keys)
    check('nonempty-bucket-delete-rejected','BucketNotEmpty' in api('s3api','delete-bucket','--bucket',b,ok=False).get('error',''))
    api('s3api','delete-object','--bucket',b,'--key','raw/empty');check('selective-delete',get(b,'raw/empty',False)[1] is None and get(b,'raw/binary')[1]==b'changed')
    api('s3api','put-bucket-versioning','--bucket',b,'--versioning-configuration','Status=Enabled')
    v1=put(b,'versioned',b'v1');v2=put(b,'versioned',b'v2');delete=api('s3api','delete-object','--bucket',b,'--key','versioned')
    versions=api('s3api','list-object-versions','--bucket',b,'--prefix','versioned');h.save('versioning',versions)
    check('versions-delete-marker',len(versions.get('Versions',[]))==2 and len(versions.get('DeleteMarkers',[]))==1,{'put1':v1,'put2':v2,'delete':delete})
    # A fresh service process in memory mode is an independent reset.
    h.inner('restart','floci');h.wait(lambda:h.api('describe-vpcs',check=False).get('Vpcs') is not None)
    check('memory-restart-reset',api('s3api','list-buckets').get('Buckets')==[])
    api('s3api','create-bucket','--bucket',b)
    runtime='public.ecr.aws/lambda/python:3.12'
    pinned_runtime='public.ecr.aws/lambda/python@sha256:238f6bfd2c1c188aff3955c2f7ceb767fe9da1b3597d84264426a11690fcf2d7'
    h.inner('pull',pinned_runtime,timeout=300)
    h.inner('tag',pinned_runtime,runtime)
    image=json.loads(h.inner('image','inspect',runtime).stdout);h.save('lambda-runtime-image',image)
    digest=image[0]['RepoDigests'][0];h.inner('tag',digest,runtime)
    code='''import json, os, urllib.parse, boto3, time
from botocore.config import Config
count=0
def handler(event,context):
 global count
 count+=1
 if event.get('fail'): raise ValueError('intentional-handler-failure')
 if event.get('sleep'): time.sleep(4)
 if 'Records' in event:
  s=boto3.client('s3',endpoint_url='http://172.17.0.1:4566',aws_access_key_id='test',aws_secret_access_key='test',region_name='us-east-1',config=Config(s3={'addressing_style':'path'},connect_timeout=2,read_timeout=3,retries={'max_attempts':0}))
  for r in event['Records']:
   b=r['s3']['bucket']['name'];k=urllib.parse.unquote_plus(r['s3']['object']['key'])
   data=s.get_object(Bucket=b,Key=k)['Body'].read()
   s.put_object(Bucket=b,Key='processed/'+k[len('incoming/'):],Body=b'PROCESSED:'+data.upper())
  return {'records':len(event['Records'])}
 return {'value':event['value']*2,'count':count,'revision':1}
'''
    def deploy(code):
        z=h.OUT/'function.zip'
        with zipfile.ZipFile(z,'w') as f:f.writestr('main.py',code)
        return 'fileb://'+str(z)
    arn=api('lambda','create-function','--function-name','mq-transform','--runtime','python3.12','--handler','main.handler','--role','arn:aws:iam::000000000000:role/test','--timeout','2','--memory-size','128','--zip-file',deploy(code))['FunctionArn']
    def invoke(payload,name='mq-transform'):
        f=h.OUT/'response.json';r=api('lambda','invoke','--function-name',name,'--payload',json.dumps(payload),f,ok=False)
        body=json.loads(f.read_text()) if f.exists() and 'rc' not in r else None
        h.save('last-invoke',{'metadata':r,'body':body});return r,body
    r,x=invoke({'value':3});check('real-lambda-input-output',r.get('StatusCode')==200 and x and x.get('value')==6,{'metadata':r,'body':x})
    r,y=invoke({'value':5});check('repeat-observable-state',y and y.get('value')==10 and y.get('count')==2,{'metadata':r,'body':y})
    for label,payload in [('invalid-input',{}),('handler-failure',{'fail':True}),('timeout',{'sleep':True})]:
        r,x=invoke(payload);check(label,r.get('StatusCode')==200 and bool(r.get('FunctionError')),{'metadata':r,'body':x})
    r,x=invoke({},'mq-absent');check('missing-function','ResourceNotFoundException' in r.get('error',''))
    api('lambda','update-function-code','--function-name','mq-transform','--zip-file',deploy(code.replace("'revision':1","'revision':2")))
    r,x=invoke({'value':7});check('updated-code',x and x.get('revision')==2,{'metadata':r,'body':x})
    api('lambda','add-permission','--function-name','mq-transform','--statement-id','s3','--action','lambda:InvokeFunction','--principal','s3.amazonaws.com','--source-arn','arn:aws:s3:::'+b)
    config={'LambdaFunctionConfigurations':[{'Id':'incoming-only','LambdaFunctionArn':arn,'Events':['s3:ObjectCreated:*'],'Filter':{'Key':{'FilterRules':[{'Name':'prefix','Value':'incoming/'}]}}}]}
    api('s3api','put-bucket-notification-configuration','--bucket',b,'--notification-configuration',json.dumps(config))
    for data in [b'hello event',b'modified event']:
        put(b,'incoming/한글 input.txt',data);start=time.monotonic();actual=None
        while time.monotonic()-start<30:
            actual=get(b,'processed/한글 input.txt',False)[1]
            if actual==b'PROCESSED:'+data.upper():break
            time.sleep(.5)
        check('event-pipeline-'+data.decode(),actual==b'PROCESSED:'+data.upper(),{'seconds':round(time.monotonic()-start,2),'actual':repr(actual)})
    put(b,'other/negative.txt',b'no-trigger');start=time.monotonic();unexpected=False;polls=0
    while time.monotonic()-start<6:
        polls+=1
        if get(b,'processed/negative.txt',False)[1] is not None:unexpected=True;break
        time.sleep(.5)
    check('nonmatching-prefix-negative',not unexpected,{'seconds':round(time.monotonic()-start,2),'polls':polls})
    inspect=json.loads(h.inner('inspect',*h.inner('ps','-aq').stdout.split()).stdout);h.save('inner-service-inspect',inspect)
    check('nested-no-published-ports',all(not x['HostConfig'].get('PortBindings') for x in inspect))
    h.save('summary',{'checks':len(checks),'passed':sum(x['passed'] for x in checks),'failed':[x['name'] for x in checks if not x['passed']]})

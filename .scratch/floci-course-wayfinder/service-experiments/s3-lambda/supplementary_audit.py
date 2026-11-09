"""Independent derived checks. Original raw checks/summary remain immutable."""
import json,pathlib,sys
p=pathlib.Path(sys.argv[1]);load=lambda f:json.loads((p/(f+'.json')).read_text(encoding='utf-8'))
c={x['name']:x for x in load('checks')};before,after=load('host-context-before'),load('host-context-after')
keys=c['same-event-no-extra-output-keys']['detail'];events=load('events')
exact_get=[x for x in events if x['label']=='s3api:get-object' and '--key' in x['argv'] and x['argv'][x['argv'].index('--key')+1]=='processed/한글 input.txt']
list_events=[x for x in events if x['label']=='s3api:list-objects-v2' and x['argv'][x['argv'].index('--bucket')+1]=='mq-supplement' and x['argv'][x['argv'].index('--prefix')+1]=='processed/']
listings=[json.loads(x['stdout']) for x in list_events]
result={'raw_matrix_passed':sum(x['passed'] for x in c.values()),'raw_matrix_total':len(c),
        'bridge_inspect_equal':before['bridge']==after['bridge'],
        'docker_context_equal':before['context']==after['context'],
        'docker_engine_id_equal':before['info']['ID']==after['info']['ID'],
        'exact_unicode_output_gets_succeeded':len(exact_get)==2 and all(x['rc']==0 for x in exact_get),
        'one_output_key_after_each_replay':len(keys)==2 and all(len(x)==1 for x in keys),
        'default_cli_paginated_aggregate':len(listings)==2 and all(not any(flag in e['argv'] for flag in ['--no-paginate','--max-items','--query','--starting-token']) for e in list_events) and all(len(x.get('Contents',[]))==1 and not x.get('NextToken') and not x.get('NextContinuationToken') for x in listings),
        'same_output_bytes_after_each_replay':c['same-event-deterministic-output']['passed']}
result['derived_no_extra_output_keys']=all(result[k] for k in ['exact_unicode_output_gets_succeeded','one_output_key_after_each_replay','default_cli_paginated_aggregate','same_output_bytes_after_each_replay'])
(p/'supplementary-audit.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))

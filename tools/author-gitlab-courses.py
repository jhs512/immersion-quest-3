"""Reproducible authoring for the user-authorized GitLab migration and CI lesson."""
import copy
import json
from pathlib import Path
import uuid
from lesson_prd import approve as approve_document
from narration_review import context_sha256, prompts

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'tools/redesigned_lessons'
def read(path): return json.loads((ROOT/path).read_text(encoding='utf-8'))
def write(path,value):
    path=ROOT/path;path.parent.mkdir(parents=True,exist_ok=True)
    if path.name=='narration-openings.json':
        # One lesson per line, matching the hand-maintained layout.
        text='{\n'+',\n'.join(f'  {json.dumps(k,ensure_ascii=False)}: {json.dumps(v,ensure_ascii=False)}' for k,v in value.items())+'\n}\n'
        path.write_text(text,encoding='utf-8',newline='\n');return
    # The narration ledger is stored with one-space indentation; keep it so reruns do not restamp the whole file.
    path.write_text(json.dumps(value,ensure_ascii=False,indent=1 if path.name=='narration-review.json' else 2)+'\n',encoding='utf-8',newline='\n')
IDS_PATH='tools/gitlab-course-ids.json'
IDS=read(IDS_PATH) if (ROOT/IDS_PATH).exists() else {}
def uid(name,prefix):
    if name not in IDS:
        IDS[name]=prefix+'_'+str(uuid.uuid4());write(IDS_PATH,IDS)
    return IDS[name]
def approve(document,by,evidence):
    # Append to the existing approval provenance instead of replacing earlier user decisions.
    previous=document.get('approval') or {}
    old_by,old_evidence=previous.get('by','').strip(),previous.get('evidence','').strip()
    if old_by:by=old_by if by in old_by else old_by+' / '+by
    if old_evidence:evidence=old_evidence if evidence in old_evidence else old_evidence+' '+evidence
    document['approval']={'status':'draft'}
    return approve_document(document,by,evidence)
EVIDENCE='2026-10-29 사용자: 기본 GitHub를 쓰는 수업을 모두 GitLab 기반으로 바꾸고 워크플로 수업도 기획해서 추가하라고 직접 지시했어요. 로그인 입력 없는 로컬 실습과 제작·검증·게시 범위의 위임이에요. 개별 문장을 사용자가 검수했다고 주장하지 않아요.'
def host_text(x):
    if isinstance(x,str):return x.replace('GitHub Flow','GitLab 흐름').replace('GitHub','GitLab').replace('깃허브','깃랩').replace('PR','MR').replace('MRD','PRD')
    if isinstance(x,list):return [host_text(v) for v in x]
    if isinstance(x,dict):return {k:(v if k in ('policy_snapshot','approval') else host_text(v)) for k,v in x.items()}
    return x
def say(text,target):return dict(action='say',text=text,target=target)
def bash(command,result):return [dict(action='bash_command',command=command,target='#git-demo-terminal'),say(result,'#git-demo-terminal')]
def task(id,title,background,commands,results,goal):
    instructions='\n'.join(f'{i+1}. `{command}`를 실행하세요.' for i,command in enumerate(commands))
    return dict(id=id,title=title,goal=background+'\n\n**할 일**\n\n'+instructions+f'\n{len(commands)+1}. 결과를 확인하고 제출하세요.',
        language='git',starter_code='',solution='\n'.join(commands),tests=[],required=True,
        git_terminal=dict(gitlab=dict(stage=goal),files={'memo.txt':'기본 메모\n'},workspace_group='gitlab-mr',workspace_revision='gitlab-mr-1'),
        narration=[say(background.split('\n')[0],'text:'+background.split('\n')[0])]+[action for c,result in zip(commands,results) for action in bash(c,result)])

catalog=read('tools/redesigned_courses/catalog.json'); java=catalog['courses'][0]
old=read('tools/redesigned_lessons/github_pr/content.json')
prd=host_text(read('tools/redesigned_lessons/github_pr/approved-prd.json'))
oldtasks=old['tasks'][:8]
new=[]
specs=[
('GitLab에 비공개 프로젝트를 만드세요','메모 파일의 기본 커밋을 준비했어요. 이번에는 이 컴퓨터의 GitLab에 공유할 프로젝트를 만들어요.\n회원가입과 로그인은 앱이 실습 계정으로 연결해요. MQ3_REPO는 이번 회차의 고유한 이름이에요. --skipGitInit는 이미 있는 로컬 저장소를 다시 만들지 않는 옵션이에요.',
 ['glab repo create "$MQ3_REPO" --private --defaultBranch main --skipGitInit','git remote add origin "$MQ3_GITLAB/$MQ3_NAMESPACE/$MQ3_REPO.git"','git remote -v'],
 ['GitLab 프로젝트만 생겼어요. 아직 로컬 커밋은 전송하지 않았어요.','origin을 이 프로젝트의 HTTP 주소에 연결했어요.','origin에 로컬 GitLab 주소가 보이면 연결된 거예요.'],'repository'),
('main의 기록을 GitLab에 보내세요','GitLab 프로젝트는 아직 비어 있어요. 팀이 받을 기본 main의 커밋을 보내세요.\n앞 단계에서 연결한 origin을 그대로 써요. -u는 main이 주고받을 원격 브랜치를 기억하게 해요.',
 ['git push -u origin main','glab repo view'],['처음 준비한 main 커밋이 GitLab에 올라갔어요.','저장소 정보를 읽어 방금 보낸 대상이 맞는지 확인해요.'],'main_pushed'),
('feature 브랜치로 옮기세요','main을 보존한 채 메모를 고칠 작업 공간이 필요해요. feature 브랜치를 만드세요.',
 ['git switch -c feature','git branch'],['새 feature를 만들고 그 브랜치로 옮겼어요.','별표가 feature 앞에 있으면 여기서 다음 커밋을 만들게 돼요.'],'branch'),
('feature에 메모 변경을 기록하세요','팀원이 함께 볼 문구로 바꾸세요. main의 메모는 아직 바꾸지 않아요.',
 ["printf '함께 읽는 메모\\n' > memo.txt",'git add memo.txt','git commit -m "메모 안내 개선"'],['작업 파일의 내용이 함께 읽는 메모로 바뀌었어요.','바꾼 파일을 다음 커밋에 담았어요.','feature에 새 커밋이 생겼어요. 아직 GitLab으로 보내지는 않았어요.'],'committed'),
('feature도 GitLab에 보내세요','수정한 feature는 아직 내 컴퓨터에만 있어요. GitLab이 두 브랜치를 비교할 수 있게 보내세요.',
 ['git push -u origin feature','git branch -r'],['feature의 새 커밋이 원격에도 생겼어요.','origin/main과 origin/feature는 원격 브랜치의 위치를 기억한 이름이에요.'],'feature_pushed'),
('MR로 main에 변경을 제안하세요','MR은 작업 브랜치의 변경을 다른 브랜치에 합치자는 요청이에요. feature에서 main으로 요청하세요.\nsource는 보낼 브랜치, target은 받을 브랜치예요. 요청을 만드는 것과 병합하는 것은 달라요.',
 ['glab mr create --source-branch feature --target-branch main --title "메모 안내 개선" --description "메모 문구를 바꿨어요." --yes','glab mr view'],['feature를 main에 합치자는 실제 MR이 열렸어요.','MR 주소와 열린 상태를 확인해요. main은 아직 기본 메모를 가리켜요.'],'merge_request'),
('MR의 바뀐 줄을 확인하세요','합치기 전에 무엇이 빠지고 들어가는지 읽으세요. 한 실습 계정으로 개발자와 검토자 역할을 번갈아 맡아요.\n자기 MR의 정식 승인 리뷰를 흉내 내지 않고 변경 내용을 직접 확인해요.',
 ['glab mr diff','glab mr view'],['기본 메모가 빠지고 함께 읽는 메모가 들어오는 차이를 읽어요.','변경을 읽어도 MR은 아직 열린 상태예요. 병합은 다음 행동이에요.'],'reviewed'),
('MR을 병합하고 로컬 main에도 받으세요','검토한 변경을 GitLab의 main에 합치세요. 그다음 내 컴퓨터의 main에도 받아야 해요.',
 ['glab mr merge --yes','git switch main','git pull','cat memo.txt'],['GitLab에서 MR이 병합됐어요. 이 순간에는 내 로컬 main이 그대로예요.','로컬 main으로 돌아왔어요.','원격에서 병합한 기록을 로컬 main으로 받았어요.','함께 읽는 메모가 보이면 원격의 병합 결과를 내 main에서도 읽은 거예요.'],'merged')]
for oldtask,spec in zip(oldtasks,specs):new.append(task(oldtask['id'],*spec))
final_id=uid('mr-final','stp')
final=task(final_id,'새 프로젝트에서 변경 제안부터 병합까지 마치세요','새 메모 프로젝트에서 혼자 전체 흐름을 완성하세요.\n비공개 프로젝트를 만들고 main을 보내세요. feature에 함께 읽는 메모를 커밋해 보내고 MR의 변경을 확인한 뒤 병합하세요. 로컬 main에도 병합 결과를 받아야 해요.',
 [*specs[0][2][:2],specs[1][2][0],specs[2][2][0],*specs[3][2],specs[4][2][0],specs[5][2][0],'glab mr diff','glab mr merge --yes','git switch main','git pull'],
 ['새 비공개 프로젝트를 만들었어요.','origin을 연결했어요.','기본 main을 보냈어요.','feature에서 작업해요.','메모를 바꿨어요.','다음 커밋에 담아요.','feature에 기록했어요.','작업 브랜치를 보냈어요.','main으로 변경을 제안했어요.','MR의 실제 차이를 읽어요.','원격에서 병합했어요.','로컬 main으로 돌아와요.','병합 결과를 받았어요.'],'final')
final['goal']=final['goal'].split('**할 일**')[0]+'**할 일**\n\n1. 고유한 비공개 프로젝트에 main과 feature를 보내세요.\n2. feature의 메모를 함께 읽는 메모로 커밋하고 MR을 만드세요.\n3. MR의 변경을 직접 확인한 뒤 병합하세요.\n4. 로컬 main으로 결과를 받아 내용을 확인하고 제출하세요.'
final['git_terminal']['workspace_group']='gitlab-mr-final'
new.append(final)
authored=host_text(old);authored['tasks']=new
authored['description']='로그인 입력 없이 로컬 GitLab에서 프로젝트를 만들어요. 작업 브랜치의 변경을 MR로 검토하고 병합한 결과를 받아요.'
prd['title']='GitLab · MR로 변경을 검토하고 합쳐요';prd['audience']='Git 브랜치·병합·리모트를 익힌 학습자'
prd['objectives']=['로컬 GitLab 프로젝트와 내 저장소를 연결해요.','작업 브랜치를 MR로 제안하고 실제 변경을 읽어요.','원격의 병합 결과를 로컬 main에도 받아요.']
authored['presentation']['objectives']=prd['objectives']
for chapter in prd['chapters']:
    chapter['title']='GitLab에서 변경을 제안하고 받아요';chapter['objectives']=prd['objectives']
    authored['presentation']['chapters'][chapter['id']]=prd['objectives']
    for i,unit in enumerate(chapter['units']):
        unit['premise']='메모 커밋을 같은 로컬 GitLab 프로젝트에 보내요. 실습 계정은 자동 연결돼요.' if i==0 else 'GitLab의 두 브랜치를 비교해 MR을 열고 병합한 뒤 로컬에 받아요.'
prd['prerequisites']=['Git 기초·브랜치·리모트를 익혔어요.','Docker Desktop을 실행할 수 있어요. GitLab 로그인 입력은 필요 없어요.']
prd['sources']=[dict(url='https://docs.gitlab.com/cli/repo/create/',checked_at='2026-10-29',finding='공식 glab으로 프로젝트를 만들고 skipGitInit로 로컬 폴더 생성 질문을 생략해요.',certainty='공식 문서와 실제 CLI를 확인해요.'),dict(url='https://docs.gitlab.com/api/merge_requests/',checked_at='2026-10-29',finding='MR의 브랜치·커밋·상태를 실제 API로 판정해요.',certainty='공식 API 명세를 사용해요.')]
prd['scope']=['기존 여덟 개념 단계와 새 독립 종합 도전을 로컬 GitLab에서 실행해요.']
prd['out_of_scope']=['외부 개인 저장소·조직 저장소·GitHub 계정을 사용하지 않아요.','한 계정의 자기 승인 리뷰를 다른 검토자의 승인으로 표현하지 않아요.']
prd['grading']=['프로젝트·브랜치 SHA·MR 상태·실제 diff 명령·로컬 main의 결과를 함께 검사해요.']
prd['narration']=['학생 저장소와 다른 회차에서 로컬 GitLab 명령을 실행하고 관찰해요.']
prd['reset']=['첫 단계와 독립 종합 도전에서 새 고유 프로젝트 이름으로 시작해요. 기존 프로젝트 기록은 보존해요.']
step_lookup={t['id']:t for t in new}
for chapter in prd['chapters']:
    for unit in chapter['units']:
        unit['steps']=[step for step in unit['steps'] if step['id'] in {t['id'] for t in oldtasks}]
        for step in unit['steps']:
            t=step_lookup[step['id']];step.update(title=t['title'],core_flow=t['goal']+'\n실제 명령: '+t['solution'])
            step['objectives']=[t['title'].removesuffix('세요')+'는 이유와 결과를 확인해요.']
        authored['presentation']['units'][unit['id']]['premise']=unit['premise']
last=prd['chapters'][-1]['units'][-1]
last['steps'].append(dict(id=final_id,title=final['title'],objectives=['새 프로젝트에서 MR 생성·검토·병합과 로컬 반영을 스스로 연결해요.'],core_flow=final['goal']+'\n'+final['solution'],complexity=dict(new_concepts=[],prerequisite_experience='앞선 여덟 단계의 MR 흐름',changed_condition='새 프로젝트에서 명령 순서를 직접 구성해요.',observable_evidence='병합된 MR과 같은 커밋을 로컬 main에서 확인해요.',learner_edited_lines=0,new_external_services=0)))
prd['representative']=dict(step_id=final_id,prompt=final['goal'],starter_state='새 로컬 저장소에 기본 메모 커밋만 있어요.',expected_action=final['solution'],acceptance='실제 GitLab MR이 병합됐고 로컬 main에서 변경 내용을 읽어요.',reset='새 회차에서는 새 프로젝트 이름을 써요.',narration='만든 기록·보낸 기록·병합한 기록을 구분해요.')
prd=approve(prd,'사용자의 GitLab 전환·제작 지시',EVIDENCE)
write('tools/redesigned_lessons/github_pr/content.json',authored);write('tools/redesigned_lessons/github_pr/approved-prd.json',prd)
row=next(x for x in java['lessons'] if x['key']=='github-pr');row.update(title=prd['title'],objectives=prd['objectives'],continuing_situation=authored['description'],revision='gitlab-mr-1')

# A genuinely incremental pipeline lesson; every hosted exercise uses a new prepared project.
check='actual=5\nif test "$actual" -eq 5; then\n  echo CHECK_OK\nelse\n  echo CHECK_FAILED\n  exit 1\nfi\n'
one='image: alpine:3.22\ncheck:\n  script:\n    - sh check.sh\n'
stages='image: alpine:3.22\nstages: [test, build]\ncheck:\n  stage: test\n  script: sh check.sh\npackage:\n  stage: build\n  script: echo PACKAGE_DONE\n'
art='image: alpine:3.22\npackage:\n  script: printf "release-ready\\n" > report.txt\n  artifacts:\n    paths: [report.txt]\n'
needs='image: alpine:3.22\nstages: [build, test]\npackage:\n  stage: build\n  script: printf "release-ready\\n" > report.txt\n  artifacts:\n    paths: [report.txt]\nverify:\n  stage: test\n  needs:\n    - job: package\n      artifacts: true\n  script: test "$(cat report.txt)" = release-ready && echo ARTIFACT_OK\n'
rules='image: alpine:3.22\ncheck:\n  script: sh check.sh\npublish:\n  script: echo PUBLISH_MAIN\n  rules:\n    - if: \'$CI_COMMIT_BRANCH == "main"\'\n'
variables='image: alpine:3.22\nvariables:\n  MESSAGE: MQ_READY\ncheck:\n  script: echo "$MESSAGE"\n'
final_yaml='image: alpine:3.22\nstages: [test, build]\ncheck:\n  stage: test\n  script: sh check.sh\npackage:\n  stage: build\n  script: printf "5\\n" > result.txt\n  artifacts:\n    paths: [result.txt]\n'
ci_specs=[
('job','검사 명령을 CI 작업에서 실행하세요','직접 실행하던 sh check.sh를 GitLab Runner가 실행하게 하세요.\nscript는 작업 컨테이너에서 실행할 명령이에요. 같은 검사 파일과 Alpine 이미지를 준비했어요.',one.replace('sh check.sh','echo 준비'),check,'.gitlab-ci.yml','echo 준비','sh check.sh',dict(jobs={'check':'success'},logs={'check':'CHECK_OK'}),'실행 주체가 내 터미널에서 Runner의 작업 컨테이너로 바뀌어요.'),
('failure','실패하는 검사를 보내고 실패 상태를 확인하세요','검사 결과가 틀리면 파이프라인이 멈추는지 확인하세요.\nactual을 4로 바꿔 보내세요. 이 문제는 실패한 파이프라인을 관찰하는 게 목표예요.',one,check,'check.sh','actual=5','actual=4',dict(pipeline_status='failed',jobs={'check':'failed'},logs={'check':'CHECK_FAILED'}),'종료 코드가 실패이면 화면의 파이프라인도 failed가 돼요.'),
('repair','실패한 검사를 고쳐 새 파이프라인을 통과하세요','앞 문제와 같은 검사를 이번에는 올바른 값으로 고치세요.\n처음 준비한 actual은 4예요. 5로 고친 커밋을 보내세요. 이전 실패 기록과 새 성공 기록은 별개예요.',one,check.replace('actual=5','actual=4'),'check.sh','actual=4','actual=5',dict(jobs={'check':'success'},logs={'check':'CHECK_OK'}),'옛 실패를 지우지 않고 새 커밋의 파이프라인이 성공해요.'),
('stages','검사가 끝난 뒤 포장 작업을 실행하세요','두 작업은 있지만 지금은 포장이 검사보다 먼저 실행돼요.\nstages의 순서를 test, build로 고치세요. 같은 단계의 작업과 다른 단계의 작업 순서는 달라요.',stages.replace('[test, build]','[build, test]'),check,'.gitlab-ci.yml','[build, test]','[test, build]',dict(jobs={'check':'success','package':'success'},job_order=['check','package']),'두 작업의 실제 시작·종료 시각으로 검사 후 포장 순서를 확인해요.'),
('artifact','작업에서 만든 파일을 산출물로 남기세요','작업 컨테이너에서 report.txt를 만들었어요. 컨테이너가 끝난 뒤에도 GitLab에서 받아야 해요.\nartifacts의 경로를 실제 만든 report.txt로 고치세요.',art.replace('paths: [report.txt]','paths: [missing.txt]'),check,'.gitlab-ci.yml','paths: [missing.txt]','paths: [report.txt]',dict(jobs={'package':'success'},artifacts={'report.txt':'release-ready'}),'작업 로그의 글자가 아니라 GitLab에 업로드된 실제 파일을 읽어요.'),
('needs','다음 작업이 앞 작업의 파일을 받게 하세요','작업마다 파일 시스템이 새로 생겨요. verify가 package의 report.txt를 받도록 설정하세요.\nneeds의 artifacts를 false에서 true로 바꾸세요.',needs.replace('artifacts: true','artifacts: false'),check,'.gitlab-ci.yml','artifacts: false','artifacts: true',dict(jobs={'package':'success','verify':'success'},logs={'verify':'ARTIFACT_OK'},artifacts={'report.txt':'release-ready'},job_order=['package','verify']),'별도 컨테이너의 verify가 파일 내용을 검사해 통과해요.'),
('rules','feature에서는 게시 작업을 만들지 마세요','검사는 모든 브랜치에서 하고 게시 작업은 main에서만 하세요.\npublish의 rules를 main 조건으로 바꾸세요. feature로 새 커밋을 보내 결과를 비교해요.',rules.replace("if: '$CI_COMMIT_BRANCH == \"main\"'",'when: always'),check,'.gitlab-ci.yml','when: always',"if: '$CI_COMMIT_BRANCH == \"main\"'",dict(jobs={'check':'success'},absent_jobs=['publish'],pipeline_ref='feature'),'feature의 파이프라인에는 검사만 있고 publish 작업은 생성되지 않아요.'),
('variables','작업 컨테이너에 전달할 값을 바꾸세요','파이프라인도 프로세스 환경 변수로 값을 전달해요.\nMESSAGE를 MQ_READY로 고쳐 작업 로그에서 그 값을 확인하세요.',variables.replace('MQ_READY','WAITING'),check,'.gitlab-ci.yml','WAITING','MQ_READY',dict(jobs={'check':'success'},logs={'check':'MQ_READY'}),'설정의 값이 작업 프로세스 환경에 들어가 script에서 읽혀요.'),
('final','실패한 검사를 고치고 결과 파일까지 남기세요','새 프로젝트에서 검사가 실패하고 산출물 경로도 틀려요.\n검사를 통과시키고 검사 다음에 포장을 실행하세요. GitLab에 남은 result.txt의 내용은 5여야 해요.',final_yaml.replace('paths: [result.txt]','paths: [missing.txt]'),check.replace('actual=5','actual=4'),None,None,None,dict(jobs={'check':'success','package':'success'},logs={'check':'CHECK_OK'},artifacts={'result.txt':'5'},job_order=['check','package']),'현재 커밋의 성공·작업 순서·실제 산출물이 모두 맞아야 도전 통과예요.')]
ci=[]
manual_id=uid('ci-manual','stp')
manual=dict(id=manual_id,title='먼저 내 터미널에서 검사 파일을 실행하세요',goal='준비한 check.sh는 값이 5인지 검사하는 작은 프로그램이에요. 먼저 자동화 없이 실행해 보세요.\n\n**할 일**\n\n1. `cat check.sh`로 검사 내용을 읽으세요.\n2. `sh check.sh`를 실행해 CHECK_OK가 나오는지 확인하세요.\n3. 확인한 결과를 제출하세요.',language='git',starter_code='',solution='cat check.sh\nsh check.sh',tests=[],required=True,
 git_terminal=dict(initial_history='uninitialized',workspace_group='ci-manual',workspace_revision='gitlab-ci-1',shell=dict(step_id=manual_id,start=dict(files={'check.sh':check},directories=[],cwd=''),demo=dict(files={'check.sh':check},directories=[],cwd=''),goal=dict(files={'check.sh':check},directories=[],cwd=''),commands=['cat check.sh','sh check.sh'],requires_vim=False)),
 narration=[say('준비한 check.sh는 값이 5인지 검사하는 작은 프로그램이에요.','text:준비한 check.sh는 값이 5인지 검사하는 작은 프로그램이에요.'),*bash('cat check.sh','실제 값과 기준값이 같아야 CHECK_OK를 출력하는 검사예요.'),*bash('sh check.sh','CHECK_OK가 보이면 이 컴퓨터에서 검사에 통과한 거예요. 다음에는 이 명령을 자동으로 실행하게 해요.')])
ci.append(manual)
observations={
 'job':['Runner가 실행할 명령을 설정 파일에 담았어요.','검사 명령을 자동화 설정에 기록한 커밋이에요.','이 커밋을 받은 GitLab이 check 작업을 예약해요.'],
 'failure':['일부러 틀린 값 4를 검사 파일에 담았어요.','실패를 확인하기 위한 새 커밋을 만들었어요.','Runner도 이 틀린 값으로 검사하므로 실패해야 해요.'],
 'repair':['actual을 5로 복구한 내용을 담았어요.','실패 원인을 고친 기록이 새 커밋으로 남았어요.','이전 실패와 별개로 수정한 커밋을 검사해요.'],
 'stages':['test를 build 앞에 둔 단계 순서를 담았어요.','파일 내용 대신 작업의 실행 순서를 바꾼 커밋이에요.','이번에는 check가 끝난 뒤 package를 시작해야 해요.'],
 'artifact':['실제 만들어지는 report.txt 경로를 등록했어요.','컨테이너 밖에 보관할 파일 경로를 커밋했어요.','package가 끝나면 GitLab에서 report.txt를 내려받을 수 있어야 해요.'],
 'needs':['앞 작업의 파일을 받겠다는 설정을 담았어요.','verify의 입력이 어디에서 오는지 기록했어요.','서로 다른 컨테이너 사이에 산출물이 전달되는지 검사해요.'],
 'rules':['main에서만 게시하는 조건을 담았어요.','게시 조건을 바꾼 커밋은 feature에만 있어요.','feature에서는 check만 만들고 publish는 제외해야 해요.'],
 'variables':['작업 프로세스에 전달할 MESSAGE 값을 담았어요.','환경 변수의 새 값을 설정 커밋에 기록했어요.','작업 컨테이너에서 MESSAGE를 읽으면 MQ_READY가 나와야 해요.'],
 'final':['검사 값과 실제 산출물 경로를 함께 담았어요.','두 결함을 고친 변경을 한 커밋으로 기록했어요.','실제 검사 통과 뒤 만들어진 result.txt까지 확인해야 도전이 끝나요.'],
}
for key,title,background,yaml,script,file,before,after,goal,meaning in ci_specs:
    id=uid('ci-'+key,'stp');commands=['git add .','git commit -m "CI 설정 변경"','git push']
    if key=='rules':commands=['git switch -c feature',*commands[:-1],'git push -u origin feature']
    changes=[(file,before,after)] if file else [('check.sh','actual=4','actual=5'),('.gitlab-ci.yml','paths: [missing.txt]','paths: [result.txt]')]
    instructions=[f'위 `{f}`에서 `{b}`를 `{a}`로 고치세요.' for f,b,a in changes]
    instructions += [f'`{c}`를 실행하세요.' for c in commands]
    instructions += ['`glab ci status --wait`로 이 커밋의 파이프라인이 끝날 때까지 기다려 결과를 확인하세요.','원하는 작업 상태와 산출물을 확인하고 제출하세요.']
    text=background+'\n이번 문제는 제공한 파일과 별도의 새 프로젝트에서 시작해요. 프로젝트 생성과 첫 커밋 전송은 준비해 뒀어요.\n\n**할 일**\n\n'+'\n'.join(f'{i+1}. {s}' for i,s in enumerate(instructions))
    actions=[say(background.split('\n')[0],'text:'+background.split('\n')[0])]
    initial_files={'.gitlab-ci.yml':yaml,'check.sh':script}
    for f,b,a in changes:
        line=initial_files[f][:initial_files[f].index(b)].count('\n')+1
        actions += [dict(action='patch_code',file=f,before=b,after=a,say=f'{f}의 {b} 부분을 {a}로 바꿔요.',target='lines:'+str(line))]
    for command in commands:actions+=bash(command,{'git add .':observations[key][0],'git commit -m "CI 설정 변경"':observations[key][1],'git push':observations[key][2],'git switch -c feature':'main은 보존하고 feature에서 확인해요.','git push -u origin feature':observations[key][2]}[command])
    actions += [say(meaning,'#git-demo-terminal')]
    expected={'.gitlab-ci.yml':yaml,'check.sh':script}
    for f,b,a in changes:expected[f]=expected[f].replace(b,a)
    ci.append(dict(id=id,title=title,goal=text,language='git',starter_code=yaml,example_files={'.gitlab-ci.yml':yaml,'check.sh':script},solution=expected['.gitlab-ci.yml'],tests=[],required=True,
        git_terminal=dict(gitlab={'stage':'pipeline','editable':['.gitlab-ci.yml','check.sh'],'pipeline_status':'success',**goal},files={'.gitlab-ci.yml':yaml,'check.sh':script},workspace_group='ci-'+key,workspace_revision='gitlab-ci-1'),narration=actions))
ci_prd=copy.deepcopy(prd);ci_prd.update(id=uid('ci-lesson','lsn'),title='GitLab CI/CD · 검사와 산출물을 자동으로 이어 가요',audience='Git push와 MR, Docker 이미지 실행을 익힌 학습자',objectives=['직접 실행하던 검사를 커밋마다 자동으로 실행해요.','실패한 로그와 설정을 연결해 고쳐요.','작업 순서·산출물 전달·실행 조건을 구분해요.'],prerequisites=['GitLab MR 수업','Docker 이미지와 컨테이너 수업'],scope=['명령 하나에서 시작해 실제 Docker Runner의 작업·실패·단계·산출물·조건을 익혀요.'],out_of_scope=['외부 서비스 배포·비밀 배포 키·호스트 Docker 소켓을 학생 작업에 연결하지 않아요.'],sources=[dict(url='https://docs.gitlab.com/ci/yaml/',checked_at='2026-10-29',finding='script·stages·artifacts·needs·rules를 단계적으로 사용해요.',certainty='공식 설정 문법과 실제 파이프라인으로 검증해요.'),dict(url='https://docs.gitlab.com/runner/executors/docker/',checked_at='2026-10-29',finding='각 작업은 별도 Docker 컨테이너에서 실행돼요.',certainty='공식 Runner 문서를 확인했어요.')])
chapter=dict(id=uid('ci-chapter','chp'),title='직접 검사에서 자동 파이프라인으로',objectives=ci_prd['objectives'],units=[])
for group,indices,title in [('run',range(0,4),'명령 하나를 자동 검사로 옮겨요'),('connect',range(4,7),'작업 순서와 파일 전달을 나눠요'),('select',range(7,10),'조건을 정하고 전체 흐름을 완성해요')]:
    steps=[]
    for i in indices:
        t=ci[i];steps.append(dict(id=t['id'],title=t['title'],objectives=[t['title']],core_flow=t['goal']+'\n관찰: 실제 작업의 상태와 로그를 현재 커밋으로 확인한다.',complexity=dict(new_concepts=[] if i==9 else [t['title']],prerequisite_experience='앞선 Git·Bash 경험과 이 수업에서 실행한 검사 명령',changed_condition=t['goal'].split('\n')[0],observable_evidence='터미널 출력' if i==0 else ci_specs[i-1][-1],learner_edited_lines=0 if i==0 else (2 if i==9 else 1),new_external_services=1 if i==1 else 0)))
    chapter['units'].append(dict(id=uid('ci-unit-'+group,'unt'),title=title,objectives=[ci[i]['title'] for i in indices],premise='작은 검사 파일을 같은 의미로 실행해요. 각 문제의 준비 파일에서 바뀐 조건 하나를 해결해요.',steps=steps))
ci_prd['chapters']=[chapter];ci_prd['representative']=dict(step_id=ci[-1]['id'],prompt=ci[-1]['goal'],starter_state='검사 값과 산출물 경로가 틀린 새 프로젝트',expected_action='검사 값을 5로 고치고 result.txt를 실제 산출물로 저장해요. 커밋하고 push해요.',acceptance='현재 커밋의 check와 package가 순서대로 성공하고 GitLab에 업로드된 result.txt가 5예요.',reset='이 문제만 새 프로젝트로 준비해요.',narration='검사 실패를 먼저 읽고 설정의 두 부분을 각각 고쳐 결과를 확인해요.')
ci_prd['grading']=['현재 HEAD SHA와 같은 파이프라인의 실제 작업 상태·실행 시각·로그·산출물을 읽어요.','성공한 다른 커밋의 파이프라인과 로컬 출력은 정답으로 인정하지 않아요.'];ci_prd['reset']=['각 문제는 별도의 고유 프로젝트와 준비 파일로 시작해요. 프로젝트 기록은 유지해요.']
ci_prd=approve(ci_prd,'사용자의 GitLab CI/CD 제작 지시',EVIDENCE)
presentation=dict(objectives=ci_prd['objectives'],chapters={chapter['id']:chapter['objectives']},units={u['id']:dict(objectives=u['objectives'],premise=u['premise']) for u in chapter['units']})
ci_authored=dict(description='내 터미널의 검사 명령을 GitLab CI/CD로 옮겨요. 실패를 고치고 작업 사이에 파일을 전달하며 커밋·설정·실행 결과를 연결해요.',tasks=ci,presentation=presentation)
write('tools/redesigned_lessons/gitlab_ci/approved-prd.json',ci_prd);write('tools/redesigned_lessons/gitlab_ci/content.json',ci_authored)
# Lessons added after the 2026-10-25 basic decision are optional with no track (tests/backend_journeys.rs).
ci_row=dict(key='gitlab-ci',id=ci_prd['id'],title=ci_prd['title'],objectives=ci_prd['objectives'],authoring_prd='tools/redesigned_lessons/gitlab_ci/approved-prd.json',continuing_situation=ci_authored['description'],revision='gitlab-ci-1',required=False,added_on='2026-10-29',origin='2026-10-29 사용자의 GitLab 기반 워크플로(CI/CD) 수업 기획·추가 지시로 새로 만든 선택 수업.',validation=dict(pilot='갓',driver='native',label='gitlab-ci'))
existing=[i for i,x in enumerate(java['lessons']) if x['key']=='gitlab-ci']
if existing:java['lessons'][existing[0]]=ci_row
else:java['lessons'].append(ci_row)

# All remaining learner-facing GitHub references in the local remote lesson become GitLab wording.
remote=host_text(read('tools/redesigned_lessons/git_remote/content.json'));remote_prd=host_text(read('tools/redesigned_lessons/git_remote/approved-prd.json'))
remote_prd=approve(remote_prd,'사용자의 GitLab 명명 전환 지시',EVIDENCE)
write('tools/redesigned_lessons/git_remote/content.json',remote);write('tools/redesigned_lessons/git_remote/approved-prd.json',remote_prd)
next(x for x in java['lessons'] if x['key']=='git-remote')['revision']='git-remote-13'
write('tools/redesigned_courses/catalog.json',catalog)
# The sequence file is hand formatted; insert textually so unrelated lines stay byte-identical.
sequence_path=ROOT/'tools/redesigned_courses/backend-sequence.json'
sequence_text=sequence_path.read_text(encoding='utf-8')
if '"gitlab-ci"' not in sequence_text:
    for a,b in [('"docker-image-container",\n','"docker-image-container", "gitlab-ci",\n'),
                ('    "docker-compose-db": [','    "gitlab-ci": ["github-pr", "docker-image-container"],\n    "docker-compose-db": ['),
                ('    "선수 관계는','    "GitLab CI/CD는 MR 흐름과 Docker 이미지·컨테이너를 익힌 뒤 둬요. 작업이 컨테이너에서 실행되기 때문이에요(2026-10-29).",\n    "선수 관계는')]:
        assert sequence_text.count(a)==1,a;sequence_text=sequence_text.replace(a,b)
    sequence_path.write_text(sequence_text,encoding='utf-8',newline='\n')
sequence=json.loads(sequence_text)
assert sequence['order'][sequence['order'].index('docker-image-container')+1]=='gitlab-ci'
assert sequence['prerequisites']['gitlab-ci']==['github-pr','docker-image-container']
classification=read('tools/redesigned_courses/lesson-classification.json')
classification['courses']['java']['lessons']['gitlab-ci']=dict(category='git',track=None,status='approved',decided_by='사용자의 GitLab CI/CD 수업 추가 지시',decided_on='2026-10-29',evidence=dict(category='버전 관리 변경을 자동 검사로 연결하는 GitLab 수업',track='기존 기본 수업과 필수 이수 범위를 보존하는 추가 수업'),title=ci_prd['title'])
classification['courses']['java']['lessons']['github-pr']['title']=prd['title'];write('tools/redesigned_courses/lesson-classification.json',classification)
challenges=read('tools/redesigned_courses/java/lesson-challenges.json');challenges['not_designated'].pop('github-pr',None)
for key,t in [('github-pr',final),('gitlab-ci',ci[-1])]:challenges['lessons'][key]=dict(task_id=t['id'],title=t['title'],reason='실제 로컬 GitLab 결과로 전체 흐름을 검증하는 독립 종합 도전이에요.')
write('tools/redesigned_courses/java/lesson-challenges.json',challenges)
openings=read('tools/redesigned_lessons/narration-openings.json');openings['github-pr']=['이 수업에서는 GitLab에서 변경을 제안하고 검토해 병합하는 흐름을 배워요.','준비한 메모 커밋을 보내고 MR을 만들어요. 병합한 뒤 내 main에도 받아 원격과 로컬의 차이를 확인해요.'];openings['gitlab-ci']=['이 수업의 목표는 검사를 자동으로 실행하고 실패 원인을 로그로 찾는 거예요.','터미널의 검사 하나에서 시작해 작업 순서·파일 전달·조건을 차례로 추가해요. 마지막에는 새 프로젝트의 파이프라인을 직접 고쳐요.'];write('tools/redesigned_lessons/narration-openings.json',openings)
fixture=copy.deepcopy(read('tests/fixtures/player-pilot/풀/course.json'));fixture['lessons'][0].update(id=ci_prd['id'],title=ci_prd['title'],revision='gitlab-ci-1',sha256='0'*64);write('tests/fixtures/player-pilot/갓/course.json',fixture)
write(IDS_PATH,IDS)
# Review covers authored meanings, not an audio listening claim. Runtime evidence is recorded separately.
ledger=read('tools/redesigned_lessons/narration-review.json')
for key,p,a in [('github-pr',prd,authored),('gitlab-ci',ci_prd,ci_authored),('git-remote',remote_prd,remote)]:
    steps=[s for c in p['chapters'] for u in c['units'] for s in u['steps']]
    for step,t in zip(steps,a['tasks']):
        digest=context_sha256(step,t)
        # Keep earlier review records when the reviewed context did not change.
        if ledger['steps'].get(t['id'],{}).get('context_sha256')==digest:continue
        ledger['steps'][t['id']]=dict(lesson=key,state='reviewed',context_sha256=digest,reviewed='2026-10-29',checked={q['text']:'Codex 문맥 검토: 주어진 상태·명령·관찰 대상의 대조가 맞는지 확인했어요. 실제 음성 청취 검토는 아니에요.' for q in prompts(t)},findings=[])
write('tools/redesigned_lessons/narration-review.json',ledger)
print('Authored GitLab MR 9 steps and CI/CD 10 steps; build and runtime validation remain required.')

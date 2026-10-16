"""Package already-authored lesson content for a browser-only preview."""
import html
import json
from pathlib import Path
import re
import shutil
import sys

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'target/web-course-preview'


def inline(value):
    return re.sub(r'`([^`]+)`',r'<code>\1</code>',html.escape(value))


def markdown(value):
    result=[]
    for block in value.split('\n\n'):
        lines=block.splitlines()
        if len(lines)>1 and lines[0].startswith('|') and re.fullmatch(r'[ |:-]+',lines[1]):
            rows=[line.strip().strip('|').split('|') for line in lines]
            result.append('<table><tr>'+''.join('<th>'+inline(c.strip())+'</th>' for c in rows[0])+'</tr>')
            for row in rows[2:]:
                result.append('<tr>'+''.join('<td>'+inline(c.strip())+'</td>' for c in row)+'</tr>')
            result.append('</table>')
        else:
            result.append('<p>'+'<br>'.join(inline(line) for line in lines)+'</p>')
    return ''.join(result)


def outcome(value):
    for before,after in [('고친다.','고쳐요.'),('남긴다.','남겨요.'),('만든다.','만들어요.'),('맞는다.','맞아요.'),('쓴다.','써요.'),('않는다.','않아요.'),('읽는다.','읽어요.'),('적는다.','적어요.'),('푼다.','풀어요.'),('한다.','해요.')]:
        if value.endswith(before):return value[:-len(before)]+after
    return value


def build():
    OUT.mkdir(parents=True,exist_ok=True)
    for name in ['index.html','style.css','app.js','python-worker.js']:
        shutil.copyfile(ROOT/'web-preview'/name,OUT/name)
    for source,name in [('assets/editor/editor.bundle.js','editor.bundle.js'),('assets/layout/split.js','split.js'),('assets/python/rich_runner.py','rich_runner.py')]:
        shutil.copyfile(ROOT/source,OUT/name)
    # Every lesson the published AICE course lists, in its order. The pilot keeps its old file name.
    course=json.loads((ROOT/'target/certification-foundations/aice-associate/course.json').read_text(encoding='utf8'))
    paths=[]
    for ref in course['lessons']:
        own=ROOT/'target/certification-foundations'/ref['id']/'lesson.json'
        paths.append(own if own.exists() else ROOT/'target/certification-pilots/aice-associate/lesson.json')
    catalog=[]
    for path in paths:
        lesson=json.loads(path.read_text(encoding='utf8'))
        for t in lesson['tasks']:
            t['goal_html']=markdown(t['goal'])
            # Pyodide has no TensorFlow: show the task, but do not offer a browser run.
            if re.search(r'(tensorflow|keras)',t['solution']):t['desktop_only']=True
            for field in ['checker','tests','narration','git_checks','web_checks','mutations']:
                t.pop(field,None)
        name='lesson.json' if lesson['id']=='aice-data-first' else lesson['id']+'.json'
        (OUT/name).write_text(json.dumps(lesson,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
        catalog.append(dict(id=lesson['id'],title=lesson['title'],path=name))
    (OUT/'catalog.json').write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    sys.path.insert(0,str(ROOT/'tools'))
    from certification_course.blueprint import build as roadmap
    plans=roadmap()
    outline=['# 두 자격증의 독립적인 전체 학습 계획','',
        '두 과정은 서로 수업·선수 지식·진도를 공유하지 않는다. 계획된 수업과 실제 구현 수업을 구분한다. 각 수업은 원리 실습, 새 문제 전이, 시험형 연습으로 연결한다.','']
    for plan in plans['courses']:
        rows=[]
        for i,item in enumerate(plan['lessons']):
            implemented=item['status']=='implemented'
            label='구현 '+str(item.get('task_count',0))+'문제' if implemented else '계획'
            available=next((c for c in catalog if c['id']==item['id']),None) if plan['id']=='aice-associate' else None
            title=html.escape(item['title'])
            if available:title=f'<a href="./?lesson={available["id"]}">{title} →</a>'
            rows.append(f'<li><span class="stage">{label}</span><h2>{i+1}. {title}</h2><p>{html.escape(" · ".join(item["topics"]))}</p><details><summary>학습 목표와 확인 방법</summary><p>{html.escape(outcome(item["evidence"]))}</p></details></li>')
        links=' · '.join('<a href="'+html.escape(url)+'" target="_blank" rel="noopener">공식 자료 '+str(i+1)+'</a>' for i,url in enumerate(plan['sources']))
        intro='각 수업은 짧은 실행과 작은 수정으로 시작해요.\n아직 만들지 않은 수업은 계획으로 표시해요.'
        exam=plan['exam'];ready=plan['readiness']
        summary=f'{exam["format"]} · {exam["minutes"]}분 · 공식 합격선 {exam["pass_score"]}점'
        page=f'''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{plan['title']} 전체 학습 계획</title><link rel="stylesheet" href="style.css"><style>body{{padding:24px;max-width:1000px;margin:auto}}h1{{font-size:28px}}ol{{padding:0;list-style:none}}li{{border:1px solid var(--line);border-radius:10px;margin:12px 0;padding:18px}}h2{{font-size:19px;margin:8px 0}}p{{line-height:1.8}}.stage{{font-size:12px;color:#a2bacb}}summary{{cursor:pointer}}</style><h1>{plan['title']} · 전체 학습 계획</h1><p>{summary}</p><p>{intro}</p><p>기초 → 원리 실습 → 시험형 연습 → 독립 모의 3세트 순서예요.</p><p>자체 준비도 목표는 모의 3회에서 각각 {ready['target_score']}점 이상이에요. 공식 합격선과는 구분해요.</p><ol>{''.join(rows)}</ol><p>{links}</p><p><a href="https://github.com/jhs512/mq3-course-{plan['id']}">이 과정의 저장소 ↗</a></p></html>'''
        (OUT/('plan-'+plan['id']+'.html')).write_text(page,encoding='utf8')
        outline.extend(['## '+plan['title'],'',summary,'','| 순서 | 수업 | 구성 | 실제 상태 |','| --- | --- | --- | --- |'])
        for i,item in enumerate(plan['lessons']):
            state='구현 '+str(item.get('task_count',0))+'문제' if item['status']=='implemented' else '계획'
            outline.append(f'| {i+1} | {item["title"]} | {" · ".join(item["topics"])} | {state} |')
        outline.extend(['','공식 근거: '+', '.join(plan['sources']),''])
    (ROOT/'docs/certification-plan.md').write_text('\n'.join(outline)+'\n',encoding='utf8')
    (OUT/'.nojekyll').touch()
    print(f'Browser preview packaged: {len(catalog)} independent AICE lessons; two separate roadmaps.')


if __name__=='__main__':
    build()

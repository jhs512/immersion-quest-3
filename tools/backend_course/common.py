"""Authoring helpers. Published lessons remain standalone JSON documents."""
import hashlib
import json
from pathlib import Path
import textwrap
import re

ROOT = Path(__file__).resolve().parents[2]
LESSONS = []
REVISION = "v1.0.0"

def code(value):
    return textwrap.dedent(value).strip() + "\n"

def task(id, title, goal, solution, *, language="junit", entry="Exercise.java", files=None,
         tests=None, starter=None, checks=None, mutations=None, stages=None):
    solution = code(solution)
    if language=='web':
        # The pinned JSX compiler uses the automatic runtime; no unused React default import.
        solution=re.sub(r"import React\s*,\s*\{",'import {',solution)
        solution=re.sub(r"import React from 'react';\n",'',solution)
        if starter:
            starter=re.sub(r"import React\s*,\s*\{",'import {',starter)
            starter=re.sub(r"import React from 'react';\n",'',starter)
    if starter is None:
        starter = "class Exercise {\n    // 필요한 메서드를 여기에 작성하세요.\n}\n"
    return dict(id=id, title=title, goal=goal, language=language, entry_file=entry,
        starter_code=code(starter), solution=solution, files=files or {}, tests=tests or [],
        web_checks=checks or [], mutations=mutations or [], required=True,
        narration=[], authoring_stages=stages or [])

def junit(tests):
    return {"ExerciseTest.java": code('''
        import org.junit.jupiter.api.Test;
        import static org.assertj.core.api.Assertions.*;
        class ExerciseTest {
    ''') + tests + "\n}\n",
    "build.gradle": code('''
        plugins { id 'java' }
        repositories { mavenCentral() }
        java { toolchain { languageVersion = JavaLanguageVersion.of(25) } }
        dependencies {
            testImplementation 'org.junit.jupiter:junit-jupiter:5.13.4'
            testImplementation 'org.assertj:assertj-core:3.27.7'
            testRuntimeOnly 'org.junit.platform:junit-platform-launcher:1.13.4'
        }
        sourceSets { test { java { srcDirs = ['.']; include '*.java' } } }
        test { useJUnitPlatform() }
    '''), "settings.gradle": "rootProject.name = 'mq3-exercise'\n"}

def jt(id, title, goal, solution, tests, **kw):
    return task(id,title,goal,solution,files=junit(code(tests)),**kw)

def lesson(id, title, description, source_ids, sections, tasks, prerequisites=()):
    result=dict(schema_version=1,id=id,revision=REVISION,title=title,description=description,
        sources=[f"https://slog.gg/p/{s}" for s in source_ids],
        sections=[dict(id=f"reading-{i+1}",title=t,body=code(b)) for i,(t,b) in enumerate(sections)],tasks=tasks)
    LESSONS.append((result,list(prerequisites)))
    return result

def html(body, style="", tailwind=False):
    return ('<!doctype html>\n<html lang="ko"><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">\n'
        + ('<!-- tailwind -->\n' if tailwind else '') + f'<style>{style}</style>\n<body>\n{code(body)}</body></html>\n')

REACT_HTML=html('<div id="root"></div>\n<script src="app.js"></script>')

def react(id,title,goal,solution,checks,starter=None):
    return task(id,title,goal,solution,language="web",entry="App.jsx",files={"index.html":REACT_HTML},
        checks=checks,starter=starter or "import React from 'react';\nimport {createRoot} from 'react-dom/client';\n// 컴포넌트를 작성하세요.\ncreateRoot(document.getElementById('root')).render(<h1>준비 중</h1>);")

def check(kind,selector=None,**values):
    return dict(kind=kind,**({"selector":selector} if selector else {}),**values)

def publish_files():
    out=ROOT/'target/backend-course'
    out.mkdir(parents=True,exist_ok=True)
    refs=[]
    for content,prerequisites in LESSONS:
        folder=out/('mq3-lesson-'+content['id']);folder.mkdir(exist_ok=True)
        # Authoring stages are retained separately; runtime only sees compiled actions.
        for t in content['tasks']:
            t.pop('authoring_stages',None)
        raw=json.dumps(content,ensure_ascii=False,indent=2)+'\n'
        (folder/'lesson.json').write_text(raw,encoding='utf-8',newline='\n')
        (folder/'README.md').write_text(f"# {content['title']}\n\n{content['description']}\n\n몰입 퀘스트 3에서 풀모드 또는 복습모드로 학습해요.\n필수 문제를 모두 통과하면 수업을 완료해요.\n\n## 학습 자료\n\n"+'\n'.join(f"- [{s}]({s})" for s in content['sources'])+'\n\n원문을 바탕으로 순서·해설·독립 실습을 보강했어요.\n외부 CodePen 원본을 복제한 자료는 아니에요.\n\n진도는 수업을 포함한 코스 저장소의 공개 이슈에 남아요.\n',encoding='utf-8')
        refs.append(dict(id=content['id'],title=content['title'],repository='jhs512/'+folder.name,
            revision=REVISION,sha256=hashlib.sha256(raw.encode()).hexdigest(),prerequisites=prerequisites,required=True))
    course=dict(schema_version=1,id='java-backend',title='자바 백엔드 과정',
        description='Git과 자바에서 시작해요. TDD로 명언 앱과 계산기를 만들어요. 프론트 기초까지 이어가요.',
        repository='jhs512/mq3-course-java-backend',lessons=refs)
    folder=out/'mq3-course-java-backend';folder.mkdir(exist_ok=True)
    (folder/'course.json').write_text(json.dumps(course,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(f"{len(refs)} lessons, {sum(len(l['tasks']) for l,_ in LESSONS)} required tasks → {out}")
    return out

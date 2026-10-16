"""Small checkpoints between large projects, authored independently of blocked CodePens."""
from .common import *
from .projects import LIST

def add(id,*tasks):
    next(l for l,_ in LESSONS if l['id']==id)['tasks'].extend(tasks)

console='''
import java.util.Scanner;
import java.io.PrintStream;
class App {
    void run(Scanner input, PrintStream out) {
        // 입력 도구와 출력 도구를 받아 실제 콘솔 없이도 검사해요.
        var store = new QuoteStore();
        while (input.hasNextLine()) {
            String command = input.nextLine();
            if (command.equals("종료")) break;
            if (command.equals("등록")) {
                // 등록 명령 다음 두 줄은 내용과 작가예요.
                String content = input.nextLine(), author = input.nextLine();
                out.println(store.add(content, author) + "번 등록");
            } else if (command.equals("목록")) {
                for (var quote : store.list())
                    out.println(quote.id() + " / " + quote.author() + " / " + quote.content());
            } else if (command.startsWith("삭제?id=")) {
                try {
                    int id = Integer.parseInt(command.substring(6));
                    out.println(store.delete(id) ? id + "번 삭제" : "없는 명언");
                } catch (NumberFormatException e) { out.println("잘못된 ID"); }
            } else out.println("알 수 없는 명령");
        }
    }
}
'''
add('wise-list',task('console-flow','콘솔 명령과 저장소 연결하기','`App.run(Scanner, PrintStream)`을 구현하세요.\n등록 다음 두 줄은 내용과 작가예요.\n목록은 `ID / 작가 / 내용`을 줄마다 표시해요.\n삭제?id=숫자는 삭제하고, 종료는 반복을 끝내요.\n제공한 QuoteStore.java를 사용하세요.\n출력 문구는 검사 사례를 확인하세요.',console,language='java_project',entry='App.java',
    starter='import java.util.Scanner;\nimport java.io.PrintStream;\nclass App {\n    void run(Scanner input, PrintStream out) {\n        // 명령을 처리하세요.\n    }\n}',files={'QuoteStore.java':code(LIST),'Main.java':code('''
    class Main {
        public static void main(String[] args) {
            new App().run(new java.util.Scanner(System.in, "UTF-8"), System.out);
        }
    }
    ''')},tests=[
    dict(input='등록\n시작\n민수\n등록\n계속\n영희\n삭제?id=1\n목록\n등록\n끝\n수지\n목록\n종료\n',expected='1번 등록\n2번 등록\n1번 삭제\n2 / 영희 / 계속\n3번 등록\n2 / 영희 / 계속\n3 / 수지 / 끝\n'),
    dict(input='삭제?id=99\n삭제?id=oops\n다른명령\n종료\n',expected='없는 명언\n잘못된 ID\n알 수 없는 명령\n')]))

add('react-components',react('reusable-links','목적지가 다른 링크 컴포넌트','Link 컴포넌트에 href와 children을 전달해요.\nnav 안에 `GitHub`, `React` 링크를 표시하세요.\n주소는 각각 https://github.com 과 https://react.dev 예요.', '''
import React from 'react';
import {createRoot} from 'react-dom/client';
function Link({href,children}) {
    // 링크의 내용도 props로 전달받아요.
    return <a href={href}>{children}</a>;
}
function App() {
    // 같은 컴포넌트에 서로 다른 값을 전달해요.
    return <nav><Link href="https://github.com">GitHub</Link>
        <Link href="https://react.dev">React</Link></nav>;
}
createRoot(document.getElementById('root')).render(<App/>);
''',[check('count','nav a',value=2),check('attribute','nav a:text-is("GitHub")',name='href',value='https://github.com'),check('attribute','nav a:text-is("React")',name='href',value='https://react.dev')]))

add('react-state',react('counter-updates','두 번 갱신과 홀짝 표시','p#value는 처음 0이에요. p#parity는 `짝수`예요.\nbutton#plus는 1, button#twice는 2를 더해요.\n버튼 twice에서는 함수형 상태 갱신을 두 번 해보세요.\n홀수이면 parity에 `홀수`를 표시하세요.', '''
import React,{useState} from 'react';
import {createRoot} from 'react-dom/client';
function App() {
    const [value,setValue]=useState(0);
    // 각 갱신 함수는 직전 갱신의 결과를 받아요.
    const twice=()=>{setValue(n=>n+1);setValue(n=>n+1);};
    return <main><p id="value">{value}</p><p id="parity">{value%2===0?'짝수':'홀수'}</p>
        <button id="plus" onClick={()=>setValue(n=>n+1)}>+1</button>
        <button id="twice" onClick={twice}>+2</button></main>;
}
createRoot(document.getElementById('root')).render(<App/>);
''',[check('text','#value',pattern='^0$'),check('click','#twice'),check('text','#value',pattern='^2$'),check('click','#plus'),check('text','#parity',pattern='^홀수$'),check('click','#twice'),check('text','#value',pattern='^5$')]))

add('react-effects-context',react('shared-context','두 소비자가 같은 상태 읽기','두 Counter 컴포넌트가 Context의 count를 공유해요.\n각 section.counter에 span 값과 `증가` 버튼을 둬요.\n어느 버튼을 눌러도 두 값이 함께 증가해요.', '''
import React,{useState,createContext,useContext} from 'react';
import {createRoot} from 'react-dom/client';
const CounterContext=createContext(null);
function Counter() {
    // 소비자마다 상태를 만들지 않고 Provider의 상태를 읽어요.
    const {count,setCount}=useContext(CounterContext);
    return <section className="counter"><span>{count}</span><button onClick={()=>setCount(n=>n+1)}>증가</button></section>;
}
function App() {
    const [count,setCount]=useState(0);
    // 상태 소유자는 공통 부모 한 곳이에요.
    return <CounterContext.Provider value={{count,setCount}}><Counter/><Counter/></CounterContext.Provider>;
}
createRoot(document.getElementById('root')).render(<App/>);
''',[check('count','.counter',value=2),check('click','.counter:first-child button'),check('text','.counter:first-child span',pattern='^1$'),check('text','.counter:last-child span',pattern='^1$'),check('click','.counter:last-child button'),check('text','.counter:first-child span',pattern='^2$')]),react('focus-ref','ref로 입력에 초점 주기','input#name과 button#focus를 만드세요.\n버튼 `입력으로 이동`을 누르면 입력에 초점을 주세요.\nuseRef로 실제 DOM 요소에 접근해보세요.', '''
import React,{useRef} from 'react';
import {createRoot} from 'react-dom/client';
function App() {
    // ref를 바꿔도 렌더링은 일어나지 않아요.
    const input=useRef(null);
    return <main><label htmlFor="name">이름</label><input id="name" ref={input}/>
        <button id="focus" onClick={()=>input.current?.focus()}>입력으로 이동</button></main>;
}
createRoot(document.getElementById('root')).render(<App/>);
''',[check('click','#focus'),check('focused','#name')]))

next(l for l,_ in LESSONS if l['id']=='react-effects-context')['sections'].append(dict(id='reading-ref',title='ref와 사용자 정의 훅',body='''
ref는 렌더링 사이에 값을 보관해요.
ref.current를 바꿔도 다시 그리지는 않아요.
입력에 초점을 줄 때 실제 DOM을 보관할 수 있어요.
화면에 표시할 값은 state로 관리하세요.
사용자 정의 훅은 use로 시작하는 함수예요.
훅을 묶어 같은 로직을 재사용할 수 있어요.
조심하세요. 훅 재사용은 상태 공유가 아니에요.
두 번 호출한 useState는 서로 다른 상태예요.
상태 공유는 공통 부모나 Context로 해요.
훅은 조건문·반복문 안에서 호출하지 마세요.
항상 컴포넌트나 사용자 정의 훅의 위쪽에서 호출해요.
'''))

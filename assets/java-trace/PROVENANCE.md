# 코드 흐름 보기 — 재사용한 핵심과 MQ 어댑터

출처: `C:/works/java-memory-visualizer` (같은 사용자의 Java 실행 메모리 시각화 프로젝트), 커밋 `6db15608d101422cbb63f2830fe89c91b052127c`.

| MQ 파일 | 원본 | 변경 | SHA-256 |
|---|---|---|---|
| `jmv/Instrumenter.java` | `tracer/jmv/Instrumenter.java` | 없음 | `332ad452513da7dbe2f0f96bf2a71f515ca0bf0cbf7276b517866416c4a64cbf` |
| `jmv/Tracer.java` | `tracer/jmv/Tracer.java` | 없음 | `bc213569cd2bf335da08f2b24dcc7b799af1f56a642f60321dd3937b03317e20` |
| `core/render.js` | `web/app/render.js` (TraceView) | MQ 변경 하나: `doc.language === 'python'`이면 이벤트 이름을 `함수 호출`/`예외 발생`으로, `<module>` 프레임을 `전역 코드`로 보인다(아래). 앱이 불러올 때 `import`/`export` 낱말만 뺀다(`src/java_trace.rs::viewer_script`). 원본 해시 `b4fcc7e0edc419e2fd276984782a8a7a9bed9dab9990996cf7bc8bf40fcd18a7` | `d981310239f9d5528846ef71aa73d26527c717ef462fd41f4b496e80ba68192c` |
| `core/highlight.js` | `web/app/highlight.js` | 없음(위와 같음) | `092f3fc7f041231d8cf8367115c64f5167ea94e412374bec287c826b7e70e1e4` |

`cargo test --lib java_trace`가 이 해시를 검사한다. 원본을 갱신하면 이 표와 테스트를 함께 바꾼다.

## MQ에서 새로 쓴 것

- `jmv/MqTrace.java`: 원래 앞단 `Compiler.java`(ECJ, Java 17)·`Visualizer.java`(CheerpJ 실행기)를 대신하는 어댑터. MQ 채점과 같은 JDK 25의 `javac --release 25 -g`로 학생의 `Main.java`를 컴파일하고, JDK 25(JEP 512) 규칙으로 `main`(static/인스턴스, `String[]` 유무)을 부른다. compact source file(`void main()`)도 그대로 컴파일한다. 의미를 바꾸는 소스 변환은 없다.
- `code-flow.js`·`code-flow.css`: 학습 화면의 `코드 흐름 보기` 대화상자와 MQ 테마에 맞춘 TraceView 스타일.

## MQ가 코어에 더한 것

- `core/render.js`: Python 추적(`src/python_trace.rs`, `assets/python-trace/mq_pytrace.py`)도 같은 TraceView로 그린다. 바뀐 곳은 이벤트 라벨 표 선택과 `frameTitle`의 `<module>` 한 줄뿐이고, Java 문서(`language` 없음)는 이전과 같은 글자로 그려진다.

## 쓰지 않은 것과 이유

- CheerpJ(브라우저 JVM): Java 17 런타임이라 JDK 25 문법·compact main을 실행하지 못하고, 라이선스 조건 확인이 필요하다. MQ는 데스크톱 앱이라 설치된 JDK 25로 같은 추적기를 실행한다.
- ECJ 3.33(Java 17): 채점 컴파일러(javac 25)와 다르다.
- ASM 9.7.1: JDK 25 클래스 파일(major 69)을 읽지 못한다. Maven Central의 ASM 9.9(`asm`, `asm-tree`)를 SHA-256 고정으로 처음 사용할 때 받는다(`src/java_trace.rs::ASM`, BSD-3-Clause).

## 관측 범위와 한계 (원본 trace-format의 한계를 그대로 따른다)

- 단계는 줄 진입·호출·반환·예외. 1000단계에서 기록을 멈추고 화면에 알린다. 20초 제한.
- 지역 변수 이름은 디버그 정보(`-g`)에서 온다. 객체는 그 단계에서 도달 가능한 것만 그린다. 물리 주소·GC·스레드는 보여 주지 않는다.
- compact source의 `main`이 인스턴스 메서드면 실행기가 먼저 `new Main()`을 만든다. 이 생성은 기록하지 않아 첫 단계가 `main`의 첫 줄이다.
- 채점·진도와 무관하다. 채점은 기존 `java --source 25` 실행과 검사가 그대로 판정한다.
- Python 코드 흐름은 채점과 같은 `rich_runner.py`를 `sys.settrace` 아래에서 실행해 기록한다(`src/python_trace.rs`). C 코드 흐름은 아직 제공하지 않는다(채점 컴파일러 TinyCC 0.9.27의 디버그 정보에 변수가 없어 검증 중).

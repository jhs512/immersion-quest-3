## Agent skills

### Issue tracker

Before creating or reading issues and specs, read `docs/agents/issue-tracker.md`. Work is tracked in local Markdown files under `.scratch/`.

### Triage labels

Before triaging an issue, read `docs/agents/triage-labels.md` for the default role labels.

### Domain docs

Before exploring the codebase, read `docs/agents/domain.md` for the single-context layout and domain documentation rules.

### 콘텐츠 룰

수업 내용(해설, 정답 코드, 주석)을 만들거나 고치기 전에 `docs/content-rules.md`를 읽는다. 코딩 해설은 살짝 코딩→실행을 반복하고 「조심하세요」 순간이 있어야 하며, 정답 코드에는 주석이 풍부해야 한다. 빌드가 강제한다.

### 목소리

학생에게 가는 글이나 LLM 프롬프트를 쓰기 전에 `docs/voice.md`를 읽는다. 말투·용어 규칙은 그 파일에만 있고, `tools/narrate.py`와 `src/assistant.rs`가 그 파일을 통째로 프롬프트에 넣는다. 새 LLM 호출을 만들면 같은 파일을 넣는다.

### 해설 모드 스크립트

개념 본문, 코딩 문제의 정답, 퀴즈 해설, 덱의 강사 스크립트를 바꾸기 전에 `docs/agents/narration.md`를 읽는다. 내용을 바꾸면 같은 커밋에서 `python tools/narrate.py`로 그 미션의 해설을 다시 만들고(바뀐 미션만 다시 쓴다) `python tools/build-kpc-course.py`로 확인한다.

## 모든 코스의 레벨링 원칙

수업을 만들거나 고치거나 검토할 때 아래 원칙으로 판단한다. 괄호는 원문의 위치다. 이 목록은 원문의 요약이고, 어긋나 보이면 원문이 우선한다.

1. **목표**: 수업·챕터·단원·스텝마다 학습자에게 보이는 교육 목표가 있고, 스텝의 행동과 채점이 그 목표를 직접 확인한다. (`docs/content-rules.md` 「모든 단계의 교육 목표는 필수」)
2. **기초 원리**: 개념의 원리를 최소 예제로 이해하는 것이 프로젝트 완성보다 앞선다. (content-rules 「최상위 원칙」)
3. **응집**: 수업 하나는 학습 목표 하나, 단원 하나는 이어지는 상황 하나, 스텝 하나는 새 개념 하나를 다룬다. (`CONTEXT.md` 「수업」, content-rules 「단순함과 점진적 과부하」「이해를 위한 난도 상승」)
4. **선수 관계**: 스텝이 쓰는 지식은 앞에서 다뤘거나 그 자리에서 짧게 설명한다. 선수는 도입 예제에 필요한 지식만 뜻하고, 진도 잠금으로 강제하지 않는다. (content-rules 「실습 공통」「이해를 위한 난도 상승」, `docs/curriculum/java-backend-expansion.md` 「각 개념의 도입 예제와 앱 연결을 구별하기」)
5. **필요한 결합만**: 코딩 문제는 자기 준비 자료로 시작하고 다른 문제의 결과나 이전 앱 구현을 읽어야 시작할 수 있게 하지 않는다. 학습 목표가 아닌 프레임워크·서비스·설정은 함께 올리지 않는다. (`CONTEXT.md` 「코딩 문제」, content-rules 「최상위 원칙」)
6. **점진 난도**: 가장 작은 실행 상태에서 시작해 조건을 하나씩 더하고, 원리 확인 문제 뒤에 조합·도전 문제를 둔다. 기술 개수·설정량·작성량은 난도가 아니다. (content-rules 「이해를 위한 난도 상승」「권장 교육 방식」)
7. **작은 수정과 관찰**: 학생은 준비 코드의 1~3줄을 바꾸고 정상 실행 → 조건 하나 변경 → 결과 비교 → 수정으로 관찰한다. 해설도 살짝 코딩 → 실행 → 출력 읽기를 반복한다. (content-rules 「이해를 위한 난도 상승」「1. 코딩 해설은 프로그램이 자라는 걸 보여 준다」)
8. **정답과 채점 일치**: 준비 코드는 실패하고 정답은 통과하며 흔한 오답은 거절되는지 실제 채점기로 확인한다. 해설의 결과 문장은 실제 실행 출력이다. (`docs/agents/narration.md` 「빌드 검사」, content-rules 「1.」)
9. **쓸모를 겪은 뒤 도입**: 도구·서비스·문법은 그것이 없을 때 생기는 문제를 먼저 겪게 한 뒤 하나씩 들인다. (content-rules 「이해를 위한 난도 상승」의 외부 서비스 항목, java-backend-expansion의 Kafka 문단)
10. **필요할 때만 시각화**: 값의 변화·참조 관계·호출 흐름을 출력보다 그림이 잘 보여 줄 때만 코드 흐름 보기·도표·만화를 쓴다. 그 언어·OS에서 실제로 추적되지 않거나 화면이 실제 상태를 보여 주지 못하면 쓰지 않는다. 판정과 데이터 크기 실험은 `.scratch/course-visualizer-audit/PLAN.md`. (content-rules 「권장 교육 방식」의 비주얼라이저 항목과 선택 자료 문단, 불가 환경에 쓰지 않는 기준은 사용자 결정 2026-11-02 `.scratch/course-visualizer-audit/spec.md`)
11. **학습자 상태 보존**: 해설은 학습자의 답안·입력·실습 상태를 보존한 채 시연하고 끝나면 돌려준다. 진도는 더하기만 하고, 본질이 바뀐 문제는 새 고유 코드로 만든다. (content-rules 「문제 정체성과 성취」, `CONTEXT.md` 「해설 시연」「진도」)

각 코스와 수업은 이 원칙 안에서 형식·스텝 종류·교육 방식을 스스로 정한다. (content-rules 「수업별 자율 영역」) 적용하는 규칙은 MQ 정책 문서에 있는 것뿐이다. 다른 프로젝트의 수치 상한이나 형식은 MQ 정책으로 채택된 경우에만 쓴다.

전체 코스·수업·스텝 목록과 코드 흐름 보기 상태는 `python tools/course_audit/inventory.py`가 만든다. 「전부 검토했다」는 이 목록과 대조해 말한다.

## Windows 작업 인계

사용자가 “계획 마저 진행해”라고 요청하면 `docs/curriculum/windows-handoff.md`를 먼저 읽고 현재 중단 지점부터 이어간다. 계획 파일을 읽거나 pull한 것만으로 제작을 시작하지 않는다.

## MQ 작업 실행자

MQ 작업은 기본으로 Claude Code가 한다(사용자 결정 2026-11-03). Codex는 Claude 브리지로 작업을 맡기고, 끝나면 실제 화면·테스트로 직접 검증한다. Claude 한도 초과 등으로 다른 실행자로 넘길 때는 브리지 규칙을 따른다.

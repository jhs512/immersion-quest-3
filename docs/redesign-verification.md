# 세 과정 개편 검증 기록

2026-10-19 기준. [전체 수업 구성](redesigned-courses.md)과 구분해 실행·게시·설치 검증의 범위와 한계를 기록한다.

## 제작과 게시

- 자바 백엔드 18수업·150스텝, AICE Associate 24수업·204스텝, 정보처리기사 실기 30수업·335스텝. 세 과정은 독립적이다.
- 수업별 PRD·대표 문제는 전체 재설계 위임 범위에서 승인 해시를 고정했다. 개별 수업을 사용자가 직접 검수했다고 표시하지 않는다.
- 공개 코스 저장소 세 개와 수업 저장소 72개를 게시했다. 실제 앱 로더가 불변 태그와 SHA-256을 확인해 689개의 고유 스텝을 읽었다. GitHub 진도 이슈의 생성·재조회·중복 방지·과거 완료 보존을 확인하고 검증용 이슈를 닫았다.
- Java의 현재 범위는 Git·Java·테스트·가벼운 React/Tailwind다. Spring Boot·DB는 후속 확장 범위이며 이미 구현한 수업으로 계산하지 않는다.

## 자동 검사와 실제 앱

| 범위 | 결과와 근거 |
| --- | --- |
| 최종 배포 코드의 전체 Rust 검사 | d9d5c2d의 깨끗한 소스에서 69묶음, 182 passed / 0 failed / 93 ignored, 619.93초. ignored인 실제 앱 검사는 별도로 실행했다. |
| 전체 새 수업 실행 | 2da0313 깨끗한 소스에서 추가58수업의 공개 입력·오답·해설 실행 통과. 최초14수업은 별도 통합 검사에 포함된다. 이후 구조 개선은 게시 콘텐츠의 바이트를 바꾸지 않았다. |
| 실제 GitHub 설치·진도 | 2da0313, 3코스/72수업/689스텝 및 진도 round-trip 통과, 65.35초. |
| Windows 핵심 화면과 실제 셸 | [39212491062](https://github.com/jhs512/immersion-quest-3/actions/runs/39212491062), d9d5c2d, workspace/terminal 모두 성공. 영문 Windows에서 깨지던 한글 출력은 자식 셸만 UTF-8로 초기화해 수정했다. |
| macOS ARM 구조 개선 | [39206901238](https://github.com/jhs512/immersion-quest-3/actions/runs/39206901238)의 ARM architecture job 성공. 같은 실행의 Windows 실패와 Intel 시간 초과를 전체 성공으로 바꾸어 표시하지 않는다. |
| macOS Intel 구조 개선 | 위 실행의 core23·수업 등록·업데이트·Git 상태·Python·CSV·Java·잘못된 순서·두 static수업·C다중포인터·TensorFlow가 통과했다. 전체 job은45분 제한으로 취소됐다. web/Git 검사는 별도 실행으로 대조한다. |
| 실제 React/Tailwind와 브라우저 | [39210447089](https://github.com/jhs512/immersion-quest-3/actions/runs/39210447089), Windows·Mac ARM·Intel 모두 성공. 학생의 살아 있는 iframe 보존과 새 npm/Node 경로를 검사했다. |
| Python 배포 환경과 신경망 | [39203351259](https://github.com/jhs512/immersion-quest-3/actions/runs/39203351259), 세 플랫폼의 release-runtime/neural 여섯 job 성공. Keras2 기준 환경과 실제 배포 패키지 환경을 구분했다. |
| 정처기 이론·Git | [39203806335](https://github.com/jhs512/immersion-quest-3/actions/runs/39203806335), 세 플랫폼 git/theory 여섯 job 성공. 구조 개선 후 [39212733296](https://github.com/jhs512/immersion-quest-3/actions/runs/39212733296)의 세 플랫폼 실제 Git/해설/초기화 검사도 모두 성공했다. |
| 설치 파일 사전 검사 | [39207094610](https://github.com/jhs512/immersion-quest-3/actions/runs/39207094610), Windows 설치·제거와 Mac ARM/Intel 서명·DMG·아키텍처·실행 통과. main 외 실행이므로 이 결과는 정식 릴리즈 게시를 뜻하지 않는다. |

검사에서 초기 설치를 이미 통과한 pinned compiler/JUnit 캐시를 재사용한 실행과 빈 환경 설치 검사를 구분했다. 캐시를 재사용했다고 새 학습자 자료나 답안을 공유한 것은 아니다.

## 구조 개선

수업 등록은 catalog 한곳에서 Python 제작기·Rust 등록·검증 화면으로 전달한다. 해설은 학습자 작업 공간과 세션 소유권을 모아 늦은 비동기 종료가 다음 답안을 덮어쓰지 않게 했다. 실제 동일 DOM 소유자 변경은 실패를 먼저 확인하고 수정했다. 잘못된 순서 입력의 freeze는 수정 전에도 통과했으므로 재현했다고 주장하지 않는다.

## 남은 수동 확인 범위

- 실제 음성 청취는 다운로드·캐시·재생 동기화 자동 검사와 다르다. 모든 해설을 사람이 들었다고 보고하지 않는다.
- 최초 검증에서는 실제 Windows F11과 Unicode 입력·복사만 확인했고, IME 자모 조합 및 Mac OS 키보드·clipboard는 미확인이었다. 아래 2026-10-20 추가 검증에서 이 범위를 보완했다. DOM 키 이벤트를 실제 OS 입력 통과로 계산하지 않는다.
- Windows 코드 서명과 Apple notarization은 구성되어 있지 않다. Mac의 ad-hoc codesign 검사 통과를 Developer ID 서명으로 표현하지 않는다.

원본 결과는 로컬 target/player-pilot-audit/, 진행 이력과 티켓은 .scratch/player-content-redesign/에 보관한다. 실패·취소된 실행도 삭제하지 않는다.

## 2026-10-20: Enter 연결·실제 OS 입력·설치 갱신

- 제품 소스 `6f7baa388e9b8bca44edcbc6cba1ec6c8ced1282`를 [빌드 28](https://github.com/jhs512/immersion-quest-3/releases/tag/v0.1.0-build.28)로 게시했다. [배포 실행 39272765207](https://github.com/jhs512/immersion-quest-3/actions/runs/39272765207)의 Windows·Mac ARM·release가 성공했다. 현재 배포 대상은 Windows x64와 Mac ARM이다.
- 기존 문제 화면뿐 아니라 RepositoryPlayer의 제출·읽기·다음 이동에 Enter를 연결했다. IME 확정, 길게 누른 Enter, 코드·터미널 줄바꿈, 열린 대화상자, 검사 중 중복 이동을 구분한다. Edge 브라우저 회귀 5개와 로컬 debug 앱 빌드가 통과했다.
- 별도 임시 데이터의 실제 Windows 앱에서 OS Enter 두 번으로 `값 3 확인` 제출 → 통과 창 → `값 5 확인` 이동을 확인했다. 실제 키 이벤트의 `isTrusted`도 기록했다. 테스트 답안 준비는 자동 설정이며 실제 키 입력과 구분한다.
- Windows Microsoft IME에서 `sky.press_key`의 `g k s r m f`로 `한글`을 조합했다. 실제 trusted compositionupdate와 최종 편집기 값을 확인하고, OS Ctrl+A/C → End → Ctrl+V 결과 `한글한글`도 확인했다. Git 터미널에서도 같은 조합·붙여넣기와 포커스 중 F11을 확인했다. 터미널 입력은 실행하지 않았다.
- 이전 13×13 좌표 실패를 반복하지 않았다. Windows MCP로 정상 화면 좌표·포커스를 확인한 뒤 sky의 키 입력 경로를 사용했다. Windows MCP의 영문 Shortcut 시도는 `gksrmf`가 입력돼 IME 통과로 계산하지 않았다. 이 차이를 제품 IME 오류로 보고하지 않는다.
- [Mac OS 입력 실행 39273541360](https://github.com/jhs512/immersion-quest-3/actions/runs/39273541360)에서 실제 AppKit/AX 앱의 OS Cmd+V/C 왕복 결과가 `한글 입력 검증 123`으로 일치했다. CGEvent 키 입력과 실제 시스템 클립보드를 사용했으며 DOM 입력 이벤트를 주입하지 않았다. 기존 접근성·이벤트 권한만 확인하고 새 권한을 요청하거나 보안 설정을 바꾸지 않았다.
- [최종 Mac 실행 39275300851](https://github.com/jhs512/immersion-quest-3/actions/runs/39275300851)은 같은 클립보드 검사와 편집기 포커스에서 Ctrl+Cmd+F 전체화면 왕복도 통과했다. 창 전환 후 편집기를 다시 찾아 포커스를 확인한 뒤 다음 키를 보냈다. 이전의 포커스 미복원 실패를 제품 단축키 실패로 단정하거나 성공으로 덮지 않았다. 최종 JSON은 `status=passed`, `actualOsInputVerified=true`, `nativeFullscreenShortcutVerified=true`다.
- Mac CI의 활성 입력기는 US·CharacterPalette뿐이었다. 한국어 입력기를 활성화하지 않았으며 **Mac 자모 조합은 미확인**이다. Windows IME 성공을 Mac IME 성공으로 바꿔 적지 않는다. Mac 검증용 소스는 제품 6f7baa3에 별도 테스트 파일만 더한 `codex/native-os-input-20261019`에 보관한다.
- Windows 설치 파일 SHA256 `d718b80d9f3995430b5f73975ebb6e5b098727b07abc9b72555d647abca70105`가 공개 SHA256SUMS와 일치했다. 실제 기존 설치 경로에 업데이트 exit 0, 설치 전후 답안·진도 DB 해시 동일. 설치된 정식 앱에서 새 기본 세 과정과 이전 추가 과정 목록을 확인했다. 사용자 진도는 변경하지 않고 앱을 열어두었다.
- 요약 증거는 [desktop-input-20261020.json](verification/desktop-input-20261020.json), 상세 로컬 이벤트와 설치 결과는 `target/os-input-audit/`에 보관한다. Mac 보조 검사 최초 Swift 컴파일 오류와 이후 AX 전환 검사 실패도 성공으로 계산하지 않는다.
- 종속 조건을 대조해 12·32를 완료 처리했다. 최종 티켓 상태는 **34 resolved / 0 claimed**다. 위의 미확인 범위(모든 해설의 사람 청취, Mac 자모 조합, 배포 인증 서명)는 별도로 유지한다.

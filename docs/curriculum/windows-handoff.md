# Windows 이어가기: MQ 자바 백엔드 확장

기록일: 2026-10-20. 이 파일은 컴퓨터와 대화가 바뀌어도 이어가기 위한 작업 기준이다.

## 2026-10-22 추가 기획

웹서버·가상 호스팅·포트 및 이름별 앱 분배와 Redis 기초·자료구조·활용·전달·복구를 기존 확장 계획에 구체화했다. `docs/curriculum/web-server-and-redis-foundations.md`와 `tools/redesigned_courses/java/backend-extension-plan.json`을 함께 본다. 현재 후보는 계획이며 앱 과정에 등록하거나 외부 서비스를 설치하지 않았다. 기존 JPA·Kafka 확장 범위와 `bash-environment`의 다음 제작 상태는 유지한다.

같은 기획 세션에서 사용자가 특정 수업의 풀이 기록 초기화와 코스 전체 스토리 문서 버튼을 요청했다. `docs/curriculum/player-course-management-plan.md`에 범위·원격 재동기화·코스 간 분리·학생용 이야기 원본·완료 기준을 기록했다. UI·진도 이벤트·대시보드는 아직 이 새 기획으로 변경하지 않았다.

## Git 수업 판정 재점검 (2026-10-20)

`ac4e720`에서 다시 pull 후 Git 입문·브랜치·병합·원격 수업과 PR 검사를 점검했다. Git 입문 1번의 `git status` 관찰 목표가 정확한 인수만 인정해 `git status -s`, `--short`, `-sb`, `--porcelain`도 오답 처리하던 경로를 수정했다. 파일 범위를 제한하거나 미추적 파일을 숨기는 옵션은 관찰 목표를 만족하지 않는다. 성공한 실제 명령 이력만 인정하며 자동 채점이 관찰 명령 실행을 대신하지 않는다. 메모 내용·저장소·준비 영역 조건은 그대로 검사한다.

게시된 브랜치 문제에서 `checkout feature`, `commit -am`, `merge --ff-only`, 충돌 파일의 `checkout --theirs`와 `add -A`도 실제 상태를 충족하면 통과하는 회귀 검사를 추가했다. 준비 영역에 담기 전 충돌 해결과 잘못된 브랜치·추가 커밋은 기존 검사에서 계속 거절한다. 비동기 저장 변경 중 빠진 수업 완료 문구도 저장 결과와 무관하게 메모리의 채점 결과로 즉시 표시하도록 복구했다. Windows·Mac CI에 입문/상태/병합 검사를 추가했다. 수업 본문과 해설은 변경하지 않았다. 원격 수업 8개도 실제 Git 상태·해설 저장소 분리·초기화를 두 번씩 검사하는 통합 검사를 추가했고 통과했다.

앱 원격 해설 검사는 첫 실행에서 4번의 `git show origin/main:guide.txt` 완료 확인이 실패했다. 명령 입력이 끝나기도 전에 실행 제한 시간 15초를 세던 경로를 고쳐 `typeCommand` 완료 응답 후부터 실행 시간을 세도록 했다. 입력 자체에도 별도 제한을 두며, 실패 시 debug 검사 결과에 명령·Git 실행 이력·터미널 내용을 남긴다. 재검사에서 앞 4개는 통과했으나 이후 5번의 첫 오답 제출 뒤 검사 진행이 멈춰 전체 앱 검사는 완료하지 못했다. 후속 재현은 필요하며, 원격 수업 전체 앱 검사를 통과한 것으로 보고하지 않는다. Git 입문·브랜치·병합·원격의 실제 저장소 통합 검사와 브랜치/PR 화면 검사 결과는 이 앱 전체 해설 검사의 미완료와 구분한다.

## Bash 23 동등 명령 판정 (2026-10-20)

`60ec4ec`에서 다시 pull 후 수정했다. `ls storage/archive/`, `rm -rf storage/archive/`, `ls storage/`를 실행했을 때 `rm -r`와의 문자열 차이로 실패하던 문제다. 재귀 삭제에 한해 경로 끝 `/`·선행 `./`·따옴표와 `-rf`/`-fr`/분리 옵션/긴 옵션을 허용한다. 재귀 옵션 누락, 다른 대상, 추가 인수와 셸 구문은 동등한 명령으로 보지 않는다. 실제 파일·폴더·원본 보존 판정도 유지한다. 명령 매칭 단위 검사 3개와 실제 Bash/Vim 통합 검사 6개(전체 23스텝 및 보고된 명령 재현)를 통과했다.

## 진도 비동기 저장과 재전송 (2026-10-20)

사용자가 git pull 후 진행하도록 지시해 `fee7685`까지 받은 뒤 구현했다. 이후 `304edb0`에서 다시 pull한 뒤 로컬 저장 대기도 제거했다. 제출 진행 창은 답안 검사 중에만 표시한다. 정답 판정 즉시 메모리에 완료를 반영하고 다음 문제 이동을 허용한다. 로컬 저장과 GitHub 전송은 화면과 독립된 작업에서 수행하며 저장 결과나 실패를 제출 UI에 표시하지 않는다. 문제 통과와 수업 완료 이벤트는 `progress-events.sqlite3`의 한 트랜잭션에 기록한다. 제출 시 원격 계정 확인도 업로드 작업으로 옮겼으며, 업로드 직전 실제 gh 계정 ID를 확인하는 기존 보호는 유지한다.

업로드는 화면 컴포넌트와 독립된 작업이다. 한 전송 작업에서 총 3회 시도하며 실패 사이에 1초·3초 대기한다. 실패한 기록은 로컬에 남기고 다음 클리어와 로그인 시 다시 전송한다. 다른 저장소의 접근 실패가 정상 코스 업로드까지 막지 않는다. 사용자·코스·수업·이벤트 ID를 분리하며 여러 앱 프로세스의 업로드도 직렬화한다. 전송 확인 전에는 대기 기록을 지우지 않는다. 응답을 잃어도 같은 이벤트 ID로 재시도하므로 기존 GitHub 중복 방지를 사용한다. 전송된 이벤트도 로컬 이력으로 유지해 재접속·오래된 서버 응답으로 진도가 되돌아가지 않게 한다.

검증: 재시도 소진 후 재시작·다음 클리어 재전송, 응답 유실·수업 완료 중복 방지, 계정/저장소 분리, 느린 업로드 중 추가 클리어, 미확인 기록 보존, 실패한 저장소의 격리 단위 검사를 통과했다. 실제 Mac 앱에서는 로컬 SQLite를 잠그고 GitHub 쓰기도 강제로 실패시킨 상태에서 클리어·다음 문제 이동·재시도 중단·대기 기록 보관·다음 클리어 후 과거 기록과 수업 완료 전송까지 확인했다. 기존 Bash 부분 초기화 및 최신 제출/콘텐츠 갱신 실제 화면 검사도 통과했다.

## 빌드 48의 Mac 화면 검사 진입 오류 (2026-10-20)

빌드 48은 Windows가 통과했고 Apple Silicon의 `player_bash_native`에서 수업 진입 전에 시간 초과됐다. 실패 화면은 Bash 수업 목록에 머물렀으며 부분 초기화 검사에는 도달하지 않았다. 기존 Bash 검증 스크립트는 수업 버전 버튼을 반복 클릭해 `RepositoryPlayer`를 다시 만들면서 곧바로 학습 시작을 눌렀다. 화면 재생성과 진행 중인 수업 진입이 겹칠 수 있는 경로를 제거했다.

검증 앱을 띄우기 전에 소유 임시 세션의 `pilot-remote.json`에 등록부의 Bash 버전을 지정한다. 실제 수업 목록과 활성 학습 시작 버튼을 확인해 클릭하고, 23개 문제 화면이 열린 것을 확인한 뒤 기존 검사를 수행한다. 클릭 가능 여부 확인과 실제 클릭도 같은 폴링 콜백에서 처리해 버튼 교체 사이의 틈을 없앴다. 재시도나 대기 시간 연장으로 검사를 숨기지 않는다. 학생 앱 동작이나 수업 콘텐츠는 변경하지 않는다.

수정 후 로컬 실제 Mac 앱의 새 세션 두 개에서 Bash 3개 검사가 각각 통과했다(각 17초). Git 과정 5개 검사도 통과했다. 다음 커밋의 Windows/Apple Silicon CI와 릴리스 게시 결과를 별도로 확인한다.

최종 결과: [빌드 49 CI](https://github.com/jhs512/immersion-quest-3/actions/runs/39406343382)는 Windows·Apple Silicon·release 모두 success다. 실제 맥 화면 검사는 Bash 3개, Git 5개, Java 실행 12개, Java 인자 12개, 로딩·음성 8개로 총 40개가 통과했다. [빌드 49](https://github.com/jhs512/immersion-quest-3/releases/tag/v0.1.0-build.49)가 최신 정식 릴리스로 게시됐고 Windows 설치 파일·arm64 DMG·SHA256SUMS 세 자산을 확인했다. 게시 체크섬은 GitHub 자산의 SHA-256 digest와 일치한다. 앱 소스는 `a4bb5c7`이며 공통 부분 초기화와 NBSP 자동 보정을 포함한다. 아래 빌드 47 최신 문구는 이전 배포 이력이다.

## 공통 부분 초기화와 NBSP 자동 보정 (2026-10-20)

사용자가 Git을 포함한 모든 문제의 부분 초기화와 NBSP 자동 보정을 요청했다. 공유 실습을 첫 문제에서만 초기화하던 UI 제한을 제거했다. 현재 문제의 준비 상태(파일·폴더·Git 커밋/인덱스·현재 폴더·Vim 버퍼/모드·Java 클래스)를 새 소유 폴더에 구성한다. 완료 이벤트와 다른 문제의 답안은 지우지 않으며, 이전 공유 실습 폴더는 복구용으로 남긴다. 현재 공유 폴더는 선택한 문제의 시작 시점으로 돌아가므로 이후 단계의 파일을 동시에 유지하는 의미는 아니다.

GitHub PR은 실제 원격 저장소나 PR을 삭제/되돌리지 않는다. 문제에 들어왔을 때의 로컬 파일·Git 상태를 별도 체크포인트로 보관하고 같은 원격 저장소 이름을 유지한 채 복원한다. 체크포인트는 반복 초기화에도 유지된다. Bash 시작 폴더와 Vim 초기 버퍼를 재접속 전에도 보존한다.

터미널의 키보드·IME·붙여넣기에서 U+00A0를 일반 공백으로 바꾼다. 글자를 삭제하지 않는다. 이미 생긴 NBSP 파일명은 자동 개명하지 않으며 해당 문제 초기화로 다시 시작할 수 있다. 앞선 “붙여넣기는 원문 보존” 정책은 이 사용자 지시로 대체한다.

검증: Rust 실습/복구 31개, Chromium/WebKit의 한글·NBSP 입력 16개 통과. 실제 Mac 앱에서 Bash 9번 독립 초기화→NBSP 명령→정상 파일 제출→다시 초기화 후 완료 기록 보존, Git 중간 단계 초기화를 확인했다. 네이티브 Bash 3개·Git 과정 5개 검사가 통과했다. 새 부분 초기화 Rust 검사와 Bash 실제 화면 검사를 Windows/Apple Silicon 배포 CI에 연결했다. 빌드 47 설치 파일에는 이 수정이 없으며 후속 빌드에 포함된다.

## 최신 배포 대상: Windows와 Apple Silicon (2026-10-20)

사용자가 “인텔맥 빼자”라고 지시했다. Intel Mac을 배포 CI와 필수 설치 파일, 최신 다운로드 안내에서 제외한다. 한 줄 설치기는 Intel에서 파일 변경 전에 종료한다. 이전 Intel 릴리스와 학습자 데이터는 삭제하지 않는다. 아래의 세 플랫폼 배포 계획은 이 지시로 대체한다.

앱 바이너리가 바뀌지 않는 배포 설정·안내 변경이므로 빌드 47의 검증된 Windows/arm64 설치 파일을 사용한다. 소스 커밋은 `95be83c`이며 각 플랫폼의 기능·실제 앱·설치/패키징 게이트를 통과한 파일만 게시한다. Intel을 제외한 자산 검증과 SHA256SUMS를 다시 생성한다.

게시 완료: [빌드 47](https://github.com/jhs512/immersion-quest-3/releases/tag/v0.1.0-build.47)이 최신 정식 릴리스다. Windows 설치 파일, arm64 DMG, SHA256SUMS 세 자산의 업로드와 공개 상태를 API로 확인했다. 게시된 체크섬 파일도 로컬 생성본과 일치한다. 빌드 47의 Windows/arm64 작업은 모두 success이며 남은 Intel 작업은 사용자 지시로 중단했다. 전체 run의 canceled 상태를 두 지원 플랫폼의 실패로 해석하지 않는다. 배포 정책·안내만 바뀐 커밋은 중복 빌드를 피하도록 CI를 생략했으며 앱 소스·설치 파일은 검증된 `95be83c` 그대로다.

## 배포 재검증: Intel XGBoost와 OpenMP (2026-10-20)

빌드 46은 Windows 설치·제거와 Apple Silicon DMG 검증을 통과했고 두 Mac의 실제 앱 화면 검사도 각 36개 모두 통과했다. Intel의 마지막 Python 새 환경 검사에서 XGBoost 3.4.1이 `___kmpc_dispatch_deinit`을 찾지 못해 릴리스가 차단됐다. 앱 전용 OpenMP 14에 이 함수가 없었다.

두 CPU의 conda-forge OpenMP 21.1.8을 SHA-256으로 고정하고 구버전 14 마커를 새 설치로 간주하지 않도록 변경했다. Intel 배포본에서 해당 함수의 공개 심볼을 확인했다. 새 `.conda`의 두 zstd 아카이브(실제 라이브러리와 라이선스)는 앱 안의 Rust 디코더로 해제한다. macOS 기본 tar가 외부 zstd를 요구하는 점을 확인했으므로 Homebrew 도구에 의존하지 않는다. 기존 시스템 라이브러리와 PATH는 바꾸지 않는다.

Mac arm64의 임시 새 환경에서 OpenMP 21 설치·라이선스 추출과 전체 패키지 진단, TensorFlow·XGBoost 동시 import 검사가 69초에 통과했다. 구버전 14를 재사용하지 않고 기존 설치를 보존하는 교체 검사도 통과했다. Intel 실제 전체 검증은 다음 배포 CI에서 확인한다.

## 배포 재검증: Windows PTY 시작 응답 (2026-10-20)

빌드 45의 Windows 검사에서 응답을 완전히 제거하면 PTY가 `ESC[6n` 이후 Vim을 시작하지 못하는 차이를 확인했다. Windows에서는 Vim 상태가 아직 없는 시작 구간에만 커서 응답을 보내고, Mac에서는 보내지 않는다. 재접속 후 X 입력 확인도 고정 130ms 뒤 상태를 읽는 대신 실제 기대 버퍼가 게시될 때까지 기다린다. 수정 후 Mac 릴리스 Vim 6개 검사는 다시 통과했다. 빌드 45 Apple Silicon CI의 실제 WKWebView 검사 결과를 내려받아 Git 4개·Java 실행 12개·Java 인자 12개·로딩/음성 8개 모두 통과한 것을 확인했다. 로컬 Java 인자 시연 시간 초과는 이 CI에서 재현되지 않았다. Windows와 두 Mac 배포 게이트는 후속 커밋에서 다시 실행한다.

## Mac 인계 오류 수정 (2026-10-20)

Mac arm64에서 아래 Vim 실패 두 건을 동일하게 재현했다. 원인은 `tests/vim_practice.rs`의 화면 없는 테스트 도우미가 실제 커서 위치를 계산하지 않고 `ESC[1;1R`을 입력으로 보내는 것이었다. 이 바이트열이 입력 모드에서 F3 키로 해석되어 `<F3>`가 버퍼에 삽입됐다. 가짜 응답을 제거하고 Vim의 기본 처리를 사용한다. 앱 터미널의 실제 화면 응답과 수업 콘텐츠는 변경하지 않았다. 여섯 검사와 모든 판정 조건을 유지했다.

- 수정 전: 6개 중 2개 실패, `<F3>첫 메모`와 `임<F3>X시메모` 재현.
- 수정 후: 실제 Vim 14스텝, 미저장 버퍼·입력 모드·커서 복구를 포함한 6개 검사 통과. `--release --locked --test vim_practice`에서도 6개 모두 통과.
- Mac arm64에서 임시 폴더에 공식 JDK 25를 다운로드·검증·소스 실행했고 PATH 보존 검사를 통과했다. C 준비 후 실제 컴파일·실행과 CPU 선택 검사도 통과했다.
- `macos_runtime`, `java_launch`, `java_arguments`, `bundled_courses`, `github_pr`, `redesigned_git_branch`, `bash_basics`, `vim_practice`: 24개 통과. 실제 GitHub 저장소를 만드는 PR 검사는 기존대로 제외했다.
- Mac 설치 스크립트/릴리스 자산 검사 4개와 수업·과정 번들 `--check` 통과.

네이티브 WKWebView Git 수업 검사와 수업 로딩·환경 메뉴·Edge 음성 8개 검사는 통과했다. 추가 실행한 `player_java_arguments_native`는 6번 문제의 전체 해설이 60초 내 복귀하지 않아 실패했고, 릴리스 컴파일 종료 후 단독 재실행에서도 재현됐다. 실패 시 편집기에는 시연 코드가 일부만 입력된 상태였다. 원인은 아직 확정하지 않았다. `target/mac-handoff-native.log`, `target/mac-handoff-native-retry.log`에 로컬 결과가 있다. 이 실패를 Vim 수정으로 해결됐다고 처리하지 않는다.

Intel/Windows 실행과 세 설치 파일의 새 게시 여부는 이번 푸시의 릴리스 CI 결과로 확인한다. 아래 OpenMP/Python 전체 새 설치, C 도구가 없는 Mac의 설치 창, 첫 실행 bootstrap 및 설치기의 전체 교체 검증은 이 Vim 수정만으로 완료 처리하지 않는다.

## 최우선: Windows 검증 후 Mac에서 이어가기 (2026-10-20)

사용자의 최신 지시: “윈도우만 보고 맥에서 이어갈게”, “다 했으면 커밋/푸시”. 이 절이 아래의 이전 계획보다 우선한다. `main`을 pull해서 이어간다. 실제 저장소는 `jhs512/immersion-quest-3`이고 Windows 작업 경로는 `C:/Users/jangk/Documents/Codex/2026-10-12/immersion-quest-3`다.

이번 변경:

- 첫 실행의 Java·C·Python 자동 준비와 앱 설정의 환경 진단/설치를 연결했다. bootstrap 기록은 준비 완료를 뜻하지 않는 attempted 상태다. 실패하면 앱 설정에서 재시도한다. 개발/검증 앱에서는 자동 bootstrap을 건너뛴다.
- `src/runtime_setup.rs`가 CPU별 Temurin JDK 25를 공식 API로 내려받아 SHA-256, javac, 실제 소스 실행을 검사한 뒤 앱 전용 위치를 게시한다. 기존 시스템 Java/PATH는 바꾸지 않는다. Mac Java shim을 검사하다 불필요한 OS 설치 창을 띄우지 않도록 한다.
- Windows C는 기존 자동 TinyCC 준비를 진단에도 연결했다. Mac C는 xcode-select 설치 창을 앱에서 요청하지만 설치/약관 확인은 사용자가 한다.
- Python은 정상인 환경을 유지한다. 필요한 경우 기존 자동 설치를 호출하고 실제 패키지 import를 검사한다. Mac은 Homebrew 의존을 줄이려고 앱 전용 LLVM OpenMP 배포본과 라이선스, 자식 Python의 DYLD_LIBRARY_PATH 연결을 구현했으나 이 변경은 Mac 실기 미검증이다.
- Mac 설치 스크립트가 새 CLI를 호출한다. 구버전 앱에 새 CLI 옵션을 넘겨 GUI 프로세스가 실행되는 것을 막으려고 번들 `environment-setup-v1` 리소스를 검사한다. 구버전 분기는 기존 Python 준비 방식이다. Mac 스크립트/번들/자동 bootstrap은 Mac에서 확인해야 한다.
- Mac 키보드가 보내는 NBSP는 일반 공백으로 전달한다. 붙여넣기는 원문을 유지한다. 기존에 생긴 NBSP 파일명은 자동 변경하지 않았다. 사용자 사례 `"\302\240memo.txt"`는 실제 파일명 앞의 U+00A0다.
- 입력하라고 지시하는 문자열은 따옴표로 범위를 표시하고, 필요한 공백 위치/개수를 명시한다. 78수업 원본에서 번호 안내를 검색했고 누락된 Vim 지시를 전부 정리했다. 문자열/명령/키 자체와 채점값은 바꾸지 않았다. Vim 해설 9개와 번들을 재생성했다. 앞서 적용한 인라인 문자열 전체 선택으로 `첫 메모`와 `새 ` 모두 정확히 선택됨을 확인했다.

Windows에서 완료한 검증:

- 공식 JDK를 빈 임시 폴더에 실제 다운로드/추출해 Java 소스를 실행했다. 설치 전후 PATH가 같다.
- 빈 앱 데이터 폴더에서 C 자동 준비 후 실제 C 코드를 컴파일·실행했다.
- 별도 새 Python 3.13.13 환경에 79개 패키지를 설치하고 TensorFlow·XGBoost·표/그래프 라이브러리 전부 import하는 검사를 통과했다(169초). 학습자 환경을 지우지 않는 임시 검증이다.
- 실제 Bash 23단계를 포함한 bash_basics 4개, 실제 Vim 14단계를 포함한 vim_practice 6개, 내장 코스 설치/업데이트 1개가 통과했다.
- Windows Chromium/WebKit의 한글 조합·따옴표 보존·NBSP·붙여넣기 보존·세션 소유권·문자열 선택 검사 19개가 통과했다.
- Windows 네이티브 앱 player_loading_native의 8개 검사(코스 로딩, 메뉴의 환경 버튼, 기존 UI/음성/입력 흐름)가 통과했다. 결과는 `target/pilot-native-result.json`이다.

Mac에서 이어서 할 일 / 배포 상태:

1. 이전 커밋 `99e2d97`의 [빌드 43 CI](https://github.com/jhs512/immersion-quest-3/actions/runs/39387454490)는 Windows 성공, 두 Mac 실패, release skipped다. 최신 게시 설치 파일은 여전히 빌드 39였다. 이번 커밋을 배포 완료라고 안내하지 않는다.
2. Mac 실패는 vim_practice의 두 기존 검사다. `real_vim_checks_modes_buffers_cursor_undo_search_saving_and_exit_live`에서 버퍼가 `<F3>첫 메모`, `unsaved_text_input_mode_and_cursor_survive_reopening`에서 `임<F3>X시메모`가 된다. 테스트의 DSR 응답과 입력 모드 전환 경로를 조사하되 실제 원인은 아직 확정하지 않았다. 여섯 검사 중 저장 관련 네 검사는 Mac CI에서도 통과했다. 검사 삭제로 숨기지 않는다.
3. 위 실패를 해결한 뒤 새 자동 JDK 설치를 양쪽 CPU, macOS C 설치 요청/완료, 앱 전용 OpenMP와 Python 패키지 import, 첫 실행 bootstrap, 구버전 설치 스크립트 호환을 확인한다. 양쪽 Mac의 기존 네이티브 검사와 릴리스 3종 게이트를 통과시킨다.
4. 사용자 지시대로 Windows 검증까지만 마치고 Mac 실기 작업은 남겼다. 아래의 과거 배포 완료 이력을 이번 미배포 변경에 적용하지 않는다.

## Git 수업 개편·배포 완료 (2026-10-20, 빌드 39)

사용자의 최신 지시에 따라 Git 기본 → 브랜치 기본(4스텝) → 리모트(8스텝) → 브랜치 심화(5스텝) → 실제 GitHub PR(8스텝) 순서로 개편했다. 브랜치 문제의 기존 스텝 UUID를 유지하며 심화 부분을 별도 수업으로 옮겼다. PR은 본인 비공개 GitHub 저장소와 실제 PR을 사용하며, 저장소 삭제는 자동으로 하지 않는다. Windows의 실제 Bash PTY와 GitHub에서 8단계를 검증했고, 두 Mac의 실제 화면 검사도 통과했다.

자바 과정은 현재 24수업 211스텝, 전체 등록은 78수업 750스텝이다. 일반 계정은 리모트까지의 첫 5수업을 보고 jhs512는 전체를 본다. 세 기본 과정은 앱에 포함하며 Windows / Apple Silicon / Intel Mac 빌드 39 게시를 완료했다. 상세 근거와 기록 보존 범위는 `docs/reviews/git-course-2026-10-20.md`와 `docs/reviews/intel-mac-and-installed-courses.md`를 따른다. 아래의 22수업·원격 과정 미갱신 등 문구는 이 변경 전의 작업 이력이다. 다음 확장 후보인 bash-environment는 아직 제작하지 않았다.

## 최신 재개 기준 (2026-10-20)

사용자가 “개별 지식의 기초/원리를 예제를 통해서 이해한다는 원칙이 더 상위원칙”이라고 명시하고 “그래 쭉 진행해봐”라고 재개했다. 메모 앱은 보조 맥락이며 원리 도입에 방해되면 독립 예제를 우선한다. 이전 중단 문구는 역사 기록이다. 실행 인자를 독립시킨 java-arguments를 제작했고 다음 수업은 bash-environment다. 기존 수업별 상태를 확인하고 순차 제작·검증한다. 실행 인자 8스텝을 추가해 현재 로컬 자바 과정은 22수업 203스텝, 전체는 76수업 742스텝이다. 실제 Windows 풀이·해설·진도 검사를 통과했고 새 수업도 Mac 실제 화면 검사를 통과했다. Windows 영문 환경에서 발견한 JDK 인자 인코딩 문제도 보완했고 39353639519의 영문 Windows·Mac JDK 및 Mac 실제 화면 검사를 통과했다. 실행기와 로컬 번들이 포함된 빌드 35 설치 파일 게시도 완료했다. 원격 과정 공개 버전은 갱신하지 않았다. 다음 환경 변수 실험과 세션 계약은 docs/curriculum/bash-environment-foundations.md에 기록했다.

## Windows 재개 기록 (2026-10-20)

사용자가 “풀 하고 작업 이어가자, 맥에서 하던 작업이 있어 나한테 물어보지말고 쭉 진행”이라고 명시적으로 재개했다. 승인된 java-launch 8스텝을 제작·등록했다. 현재 자바 백엔드는 21수업 195스텝, 전체 레지스트리는 75수업 734스텝이다. 기존 수업과 문제 식별자는 유지한다.

실제 Main.java 편집기와 Bash PTY가 같은 소유 폴더를 사용한다. Enter 전달 전에 편집 내용을 저장하며, 실제 JDK 25의 java/javac 실행 기록·출력·소스/클래스 해시와 선택 답안을 함께 검사한다. 클래스 확인은 복사한 산출물에서 수행하며 컴파일하거나 학생 파일을 변경하지 않는다. 해설은 별도 폴더와 별도 편집기를 사용한다.

구현·검증 근거와 남은 범위는 `docs/reviews/java-launch-windows-2026-10-20.md`를 따른다. 아래 중단 기록은 Mac에서 인계하던 시점의 이력이며 현재 재개 지시를 대신하지 않는다. 다음 후보 수업 43개를 일괄 제작하거나 외부 서비스를 설치한 것은 아니다.

## 이전 중단 시점의 지시와 재개 조건

사용자는 첫 수업의 PRD·대표 문제에 “이 구성으로 첫 수업부터 제작”이라고 승인했다. 이후 “잠시만 계획만 세우고 진행은 하지 말아봐”라고 제작을 중지했다. 마지막 요청은 계획과 현재 변경을 커밋·푸시하여 Windows에서 pull 후 “계획 마저 진행해”라고 하면 이어갈 수 있게 하는 것이다.

**현재는 계획만 보존한다. pull 자체로 제작을 시작하지 않는다.** 사용자가 “계획 마저 진행해”라고 하면 이 파일과 아래 원본을 읽고 첫 수업 제작을 재개한다. 이미 승인된 8스텝의 제작 승인을 다시 묻지 않는다. 범위를 바꾸면 변경 부분만 검토한다. Windows로 원격 접속하거나 새 대화를 만드는 작업은 수행하지 않았다.

## 원본과 우선순위

1. `AGENTS.md`, `CONTEXT.md`, `docs/content-rules.md`, `docs/voice.md`, `docs/agents/narration.md`를 따른다.
2. 전체 계획: `docs/curriculum/java-backend-expansion.md`.
3. 후보 목록·추천 의존 관계(입력 수업 분리 후 46개): `tools/redesigned_courses/java/backend-extension-plan.json`.
4. 승인된 첫 수업: `tools/redesigned_lessons/java_launch/approved-prd.json` 및 `approved-prd.md`. `draft-prd.*`는 검토 당시 초안으로 보존한다.
5. 8스텝의 명령·기대 결과·선택지·문구 변경: `tools/redesigned_lessons/java_launch/prototype.json`.
6. 실제 JDK 검증 재현: `tools/verify-java-launch-prototype.py`.

`.scratch/`와 `target/`는 Git에서 제외된다. 이전 로컬 이슈나 검증 출력이 Windows에 없더라도 이 문서와 추적되는 원본으로 재개한다. 출력은 다시 생성한다. 새 이슈를 만들 때는 `docs/agents/issue-tracker.md`를 먼저 읽는다.

## 절대 놓치지 않을 제작 기준

목적은 이해다. 완전히 간단한 정상 예제에서 시작해 한 번에 조건 하나만 바꾼다. 기술·파일·설정·작성량으로 난도를 올리지 않는다.

- 첫 수업은 Main.java 하나, 출력 문구 하나, 외부 서비스 0개다.
- 새 개념은 스텝당 하나, 학생 수정은 보통 1~3줄이다.
- 각 스텝은 시작 상태 → 순서 있는 **할 일** → 실행 → 실제 결과 관찰을 명확히 보여 준다.
- 파일을 뒤에서 몰래 바꾸지 않는다. 제공된 준비 코드와 해설용 준비 상태는 먼저 설명한다.
- 명령 하나를 실행하고 결과를 짚은 뒤 다음 명령으로 넘어간다.
- 같은 실습 폴더를 이어 쓰고 학생의 파일·선택·진도를 보존한다. 해설은 별도 폴더에서 수행한다.
- 문구·가격·띄어쓰기·발음은 공통 정책을 따른다. Git은 “깃”, .git은 “깃 폴더”다. 불필요한 명령 인수 따옴표를 쓰지 않는다.
- 선택지만 맞혀 통과시키지 않는다. 실제 작업·산출물과 선택 답을 함께 검사한다.
- 첫 SQL에 Spring을, 첫 컨테이너에 DB·Redis·Kafka를 한꺼번에 붙이지 않는다. 전체 후보를 한 번에 구현하지 않는다.

## 현재 구현과 미구현을 구분하기

현재 자바 백엔드 과정은 **20수업 187스텝**이다. Bash 23스텝과 별도 Vim 14스텝, Git 수업과 자바 스트림 10스텝이 포함돼 있다. 기존 수업 개선, MQ 이름, 단축키·실패 표시, 실제 Vim 상태 확인 및 제출 준비 버그 수정은 작업 트리에 구현되어 이번 인계 커밋에 보존한다.

새 java-launch 수업은 **아직 앱에 등록하지 않았다.** 승인 PRD와 실행 프로토타입만 있다. `content.json`, 해설 캐시, 런타임 수업 JSON 및 새 편집기·JDK 연동은 제작 전이다. 제작 중단 직전 시도한 런타임 패치는 적용에 실패하여 파일 변경이 없었다. 승인 기록만 추가됐다.

macOS에서는 기존 기능을 실제 앱에서 확인했다. Windows 실제 동작은 미검증이다. macOS의 `/Applications/MQ.app`, 개인 데이터 폴더, 로컬 진도·실습 디렉터리는 Git에 들어가지 않는다. Windows에서는 기존 설치·데이터를 보존하며 저장소의 설치·실행 방법을 따른다. 앱 표시 이름은 MQ이며 기존 내부 식별자·데이터 경로를 이름 변경 때문에 바꾸지 않는다.

## 첫 제작 범위: 승인된 8스텝

추가 위치는 java-crud 뒤, java-testing 앞이다. 수업 ID는 `lsn_2a4d9041-b87a-401c-a0e8-6128415e6b2f`이며 원본 스텝 ID도 그대로 유지한다.

| 단계 | 학생 행동 | 확인할 차이 |
| --- | --- | --- |
| 1 | 제공된 Main.java를 cat으로 읽기 | 출력문 안의 첫 메모 위치 |
| 2 | java Main.java | 첫 메모 출력, Main.class 없음 |
| 3 | 편집기에서 첫 메모를 둘째 메모로 바꾸고 소스 실행 | 둘째 메모 출력 |
| 4 | javac Main.java 후 이미 배운 ls | Main.class 생성, 컴파일 자체는 문구를 출력하지 않음 |
| 5 | java Main | 컴파일된 클래스에서 둘째 메모 출력 |
| 6 | 소스만 셋째 메모로 수정하고 결과 예측 후 java Main | 여전히 둘째 메모, class는 바뀌지 않음 |
| 7 | javac Main.java | 바뀐 소스로 class 다시 생성 |
| 8 | java Main | 셋째 메모 출력 |

## 재개 후 작업 순서

1. Windows의 git 상태와 origin/main을 확인하고 사용자 변경을 보존한다. Rust/Cargo, JDK 25의 java와 javac, Git for Windows의 Bash·Vim 실행 경로를 확인한다. 이전 Mac 경로를 복사하지 않는다.
2. 실제 Main.java 편집기·PTY 터미널이 동일한 소유 실습 폴더를 사용하도록 최소 범위로 연결한다. 저장 완료 전에 명령이 실행되는 경쟁을 막는다. 단계 이동·앱 재실행에도 같은 폴더를 유지한다.
3. `src/shell_practice.rs`의 현재 파일 검사는 모든 파일을 UTF-8로 읽는다. Main.class는 바이너리이므로 그대로 재사용하지 않는다. 실제 class 산출물·출력을 검사하는 별도 명시적 계약을 설계한다. 타입이나 명령 기록만 보고 class가 맞다고 판정하지 않는다. 학생 코드 실행에는 시간·출력 제한과 자식 프로세스 정리를 둔다.
4. 교사용 시작 상태는 격리된 폴더에 재현한다. 6스텝은 둘째 메모로 컴파일된 class와 수정 전 소스를 준비해 수정→실행을 보여 준다. 학생의 실제 소스·class·답을 덮어쓰지 않는다. 해설 완료·중단·오류 후에도 학생 터미널이 사라지지 않아야 한다.
5. 승인 PRD와 prototype을 바탕으로 production `content.json` 및 단계별 해설을 작성한다. 한 동작→관찰→설명 순서, 주의할 지점, 하이라이트를 포함한다. 내용과 파생물 해시를 함께 갱신한다.
6. `tools/redesigned_courses/catalog.json`에 고유 pilot 키로 java-launch를 등록한다. 기존 식별자·순서를 보존하고 추가 위치만 반영한다. `tools/build-redesigned-git.py`, `tools/build-redesigned-course-bundle.py`로 빌드한다. 완료 시 해당 과정은 21수업 195스텝, 전체 레지스트리는 75수업 734스텝이어야 한다. 숫자만 바꿔 테스트를 통과시키지 않는다.
7. 실제 PTY·JDK로 8단계를 검증한다. 미실행·오답·컴파일 실패·소스만 변경·재컴파일·재접속·초기화·해설 중단을 확인한다. 해설이 학생 파일·class·선택·진도를 바꾸지 않는지도 검증한다. 기존 Bash·Vim·Git과 키보드 조합을 회귀 검사한다.
8. Windows 실제 MQ 화면에서 편집·입력·실행·제출·단계 이동 및 레이아웃을 확인한다. 로컬 앱과 과정에 반영하고 결과·한계를 기록한다. 이후 수업은 이 작은 첫 수업의 이해 흐름을 확인한 뒤 계획 순서대로 점진적으로 진행한다.

## 구현을 볼 위치

- 소유 실습 폴더·공유·복구: `src/git_practice.rs` (`GitPracticeStore`, `workspace_group`, `workspace_revision`).
- 실제 Bash 명령 완료·폴더 검사: `src/shell_practice.rs`.
- PTY와 프로세스 종료: `src/setup_terminal.rs`.
- 학생/해설 터미널과 readiness: `src/git_terminal_ui.rs`, `assets/terminal/terminal.js`.
- 실제 Vim 검사: `src/vim_practice.rs`, `assets/vim/practice.vim`.
- 편집·선택·제출·해설 복구: `src/player_ui.rs`, `src/explanation_session.rs`.
- 해설 액션: `assets/layout/agent.js`.
- JDK 실행 경로·제한: `src/java.rs`.터미널에서도 같은 JDK의 java/javac를 사용하도록 보장한다.
- PRD 승인·난도 검증: `tools/lesson_prd.py`, `tools/test_lesson_prd.py`.
- 레지스트리·등록 검증: `tools/lesson_registry.py`, `tests/lesson_registry.rs`, `tools/test_lesson_registry.py`.

## 기본 검증 명령

저장소 루트에서 실행한다. Windows의 Python 명령이 py이면 python3 대신 py를 사용한다. prototype은 JDK를 찾도록 JAVA_HOME 또는 검사 도구의 도움말에 나온 경로 옵션을 설정한다.

```text
python3 tools/test_lesson_prd.py
python3 tools/test_lesson_registry.py
python3 tools/build-redesigned-git.py --check
python3 tools/build-redesigned-course-bundle.py --check
python3 tools/verify-java-launch-prototype.py --help
cargo test --test lesson_registry
cargo test --test bash_basics
cargo test --test vim_practice
```

이전 Mac 검증 결과를 Windows 검증으로 보고하지 않는다. prototype 검증은 앱 구현 완료를 뜻하지 않는다. 서비스·모델 설치나 원격 과정 게시를 선행하지 않는다.

## Windows에서 사용자에게 필요한 동작

기존 저장소에서 `git pull --ff-only origin main`을 실행한 뒤 이 저장소를 Codex에서 열고 **“계획 마저 진행해. docs/curriculum/windows-handoff.md부터 읽어.”**라고 요청하면 된다. pull이 로컬 수정 때문에 막히면 기존 변경을 보존하고 원인을 확인한다. 강제 초기화하지 않는다.

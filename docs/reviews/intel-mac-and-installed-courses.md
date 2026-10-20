# Intel Mac 복구와 설치된 수업 갱신

## 확인한 원인

2026-10-20 기준 배포 앱이 읽는 GitHub 자바 과정은 18수업이고 이 저장소의 현재 과정은 22수업이었다. 기존 18수업도 로컬과 해시가 달랐다. 설치 캐시가 있으면 바로 반환하는 동작까지 겹쳐 앱 파일만 업데이트해도 예전 수업이 남았다. AICE 24수업과 정처기 30수업의 원격 해시는 현재 작성본과 같았다.

macOS 배포에서 Intel 작업과 업데이트 자산 선택을 제거했고, 한 줄 설치도 arm64만 허용했다. README에는 실제 번들 이름 MQ.app 대신 예전 이름이 남았다. macOS CFBundleVersion도 빌드마다 같은 0.1.0이었다.

## 수정

- 기본 세 과정과 정확히 일치하는 버전/해시의 수업을 앱에 포함한다. 동일한 저작 데이터와 등록부를 사용한다. 새로운 수업 원본이나 네 번째 과정을 만들지 않는다.
- 기본 과정 진입과 업데이트 확인에 같은 앱 포함 데이터를 사용한다. 예전 설치 스냅샷을 원자적으로 바꾸며 과정/수업/문제 ID, 코드 초안과 GitHub 진도 이벤트는 유지한다.
- 다른 저장소의 수업이나 이전 해시를 가리키는 참조는 기존 불변 참조 규칙을 유지한다.
- Intel 네이티브 CI, x86_64 DMG, 해당 CPU의 자동 업데이트 선택을 복구한다. 세 설치 파일이 모두 있어야 release를 게시한다.
- Intel Python 3.12 / TensorFlow 2.16.2와 arm64 Python 3.13 / TensorFlow 2.21.0을 하나의 requirements에서 환경 마커로 선택한다. Intel CI에서 전체 패키지 설치와 import를 검사한다.
- README의 CPU별 설치 링크와 실제 앱 이름을 고친다. 설치기는 실행 중인 이전 앱을 닫고, 반복 설치 때 고정 백업 이름이 충돌하지 않게 보존한다. CFBundleVersion에 실제 빌드 번호를 넣는다.

## 검증

- `cargo test --locked --test bundled_courses --test content_updates`: 기본 과정 콘텐츠 다운로드를 막은 상태에서 새 설치 22/24/30수업, 예전 18수업 캐시 갱신, 코드 초안과 ID 보존, 재진입/업데이트 확인을 검사한다. 수정 전 기본 과정 다운로드 실패를 재현했고 수정 후 통과했다.
- `cargo test --release --locked --test bundled_courses`: 배포 구성에서도 앱 포함 콘텐츠와 같은 업그레이드 동작을 검사했다.
- updater / course_authoring / update_handoff 관련 테스트 통과.
- `python tools/test_macos_installer.py`: 두 CPU의 앱/Python 선택, Rosetta 오설치 차단, Bash 구문 검사 통과. 전체 macOS 설치 동작을 로컬 Windows에서 실행한 것은 아니다.
- `python tools/test_release_assets.py`: Intel DMG 누락 시 게시 차단을 수정 전 실패/수정 후 성공으로 확인했다.
- Intel macOS용 Python 3.12 바이너리 의존성 해석 성공. 실제 패키지 설치, WKWebView 수업 실행, C/Java/Python 실행, 네이티브 앱 실행과 DMG 검증은 릴리스 CI에서 두 Mac CPU별로 수행한다.

CI 완료 결과와 배포 빌드는 확인 후 덧붙인다.

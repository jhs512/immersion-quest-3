# 개발 화면 자동 갱신

로컬 API 서버가 실행된 상태에서 `scripts/start-dev.ps1`을 실행한다.
스크립트는 Dioxus CLI 0.7을 `target/dev-tools/dx.exe`에서 사용한다.
CLI가 없으면 Dioxus 공식 릴리스의 Windows 실행 파일을 그 경로에 설치한다.

개발 실행에서는 CSS를 Dioxus asset으로 로드한다. CSS와 RSX 화면 구성은
저장 시 hot reload하고, 지원하지 않는 Rust 변경은 자동 빌드와 재실행으로
반영한다. 에디터 JavaScript 변경은 `assets/editor/README.md`의 번들 명령으로
빌드해야 한다. 일반 데모와 운영 빌드는 기존처럼 CSS를 실행 파일에 포함한다.

## 자동 업데이트

`src/updater.rs`. 릴리스 워크플로가 실행 번호를 `MOLIP_BUILD`로 넣어 빌드하고(태그 `v0.1.0-build.N`의 N),
앱은 GitHub Releases API의 최신 릴리스와 자기 빌드 번호를 비교한다.

- 시작할 때 새 빌드가 있으면 묻지 않고 설치한다: 설치 파일을 앱 데이터 폴더 `updates/`에 받고, 분리된
  스크립트(Windows는 PowerShell, macOS는 sh)가 앱이 끝나기를 기다렸다가 설치하고 새 빌드를 연다.
  Windows는 Inno 설치 파일을 `/VERYSILENT`로 같은 폴더에 다시 설치하고, macOS는 DMG를 마운트해 번들을 바꾼다.
- 실행 중에는 10분마다 확인하고, 새 빌드가 나오면 상단 배너로 알린다(지금 업데이트 / 나중에).
- 작성 중인 코드와 퀴즈 답은 입력할 때마다, 진도는 제출할 때 저장되므로 언제 닫혀도 잃는 것이 없다.
- 개발 빌드(`MOLIP_BUILD` 없음, 사이드바에 「개발 빌드」)는 확인하지 않는다. `MOLIP_UPDATE_CHECK=1`로 켤 수 있다.
  Android는 APK를 손으로 설치한다.

참고: https://dioxuslabs.com/learn/0.7/essentials/ui/hotreload/

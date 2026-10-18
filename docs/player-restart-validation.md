# 재시작 검증의 격리 환경

`PilotSession`은 설치·재시작 검증용 임시 폴더를 소유한다. 자식 프로세스에 `configure`로 같은 폴더와 무작위 소유 코드를 전달하면 답안 SQLite, 설치 콘텐츠 스냅샷, 가짜 GitHub 진도를 재사용한다. 부모가 끝나면 소유 TempDir가 정리한다.

- debug 빌드의 `MOLIP_PILOT`에서만 공유 검증 폴더를 받는다.
- 이름 접두어, 정규화한 절대 경로, 일반 파일의 소유 코드가 모두 맞아야 한다. 잘못 지정한 폴더는 거절한다.
- 검증 GitHub는 로컬 `pilot-remote.json`에 원자 저장한다. 다른 저장소와 외부 gh로 요청이 넘어가지 않는다. 한 번에 한 플레이어 프로세스가 이 검증 상태를 사용한다.
- 별도 공유 환경이 없으면 기존처럼 프로세스마다 새 임시 폴더를 사용한다. 일반 사용자 데이터 경로는 바꾸지 않는다.

`tests/pilot_restart.rs`는 실제로 서로 다른 두 프로세스를 실행한다. 첫 프로세스에서 production 답안·진도 API로 저장한 내용을 다음 프로세스에서 같은 API로 읽고, 소유권이 다른 폴더는 거절하는지 확인한다.

이 검사는 설치 프로그램을 아직 실행하지 않는다. 실제 플레이어 설치 자산 교체·앱 재시작과 화면 복원 검증은 이 환경을 사용해 별도로 수행한다.

`tests/player_restart_native.rs`는 데스크톱 debug 플레이어 바이너리를 두 번 실행한다. 첫 WebView에서 한 문제를 통과한 뒤 작성하던 답안을 바꾸고, 다음 프로세스의 실제 편집기와 진도 표시를 확인한다. `target/pilot-restart-seed.json`, `target/pilot-restart-reopen.json`에 화면 검증 결과를 남긴다. CI에서는 바이너리 빌드 후 ignored 검사를 명시적으로 실행한다. 설치 프로그램을 통한 교체와 재시작은 여전히 별도다.

`tests/player_install_native.rs`는 소유 임시 폴더 안의 실제 플레이어를 교체한다. Windows는 시스템 등록과 제거 항목을 만들지 않는 별도 Inno fixture, macOS는 임시 앱 번들과 실제 DMG를 사용한다. 교체 전후 세대 파일과 다시 열린 WebView의 답안·진도를 함께 확인한다. macOS의 rollback 재실행도 격리 환경을 유지하도록 fixture Info.plist에 [LSEnvironment](https://developer.apple.com/documentation/bundleresources/information-property-list/lsenvironment)를 넣는다. 정식 배포 설치 파일이나 일반 사용자 설치 경로를 교체하지 않는다.

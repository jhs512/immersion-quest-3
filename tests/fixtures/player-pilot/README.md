# 고정된 플레이어 검증 코스·수업

이 폴더는 정식 수업이 아닌 합성 테스트 데이터다. 코스·수업의 UUID는 스냅샷 간 유지하고, 스냅샷 A는 두 스텝, B는 기존 두 스텝과 추가된 한 스텝을 가진다. 배포·계정 인증·GitHub 이슈 생성은 하지 않는다.

새 형식은 계층이 스텝의 순서와 교육 목표를 소유하고, 같은 고유 코드로 문제 실행 데이터를 참조한다. 빠진 연결·중복·순서 불일치는 허용하지 않는다. 설명 목록에 챕터라는 이름만 붙이는 방식이 아니다. 코스의 해시는 정확한 UTF-8/LF 수업 바이트에 고정한다.

Windows PowerShell에서 개발 빌드를 실행한다:

```powershell
cargo build --locked --bin molip-quest
$env:MOLIP_PILOT='1'
$env:WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS='--remote-debugging-port=9235'
$env:WEBVIEW2_USER_DATA_FOLDER=Join-Path (Get-Location) 'target/pilot-webview-profile'
& ./target/debug/molip-quest.exe
```

macOS에서는 개발 빌드에 `MOLIP_PILOT=1`을 전달해 같은 예제를 연다. UI 자동화 스크립트의 CDP 연결은 Windows WebView2 검증용이다. macOS 실제 화면 검증을 대신한다고 보고하지 않는다.

버전 a/b 버튼으로 스냅샷을 전환하고 초기화로 현재 문제 준비 코드를 복구한다. 손상 후보 버튼은 핀 해시와 맞지 않는 후보를 같은 로더에 넣어 거절을 확인하며 현재 스냅샷과 답안을 변경하지 않는다. 일반 플레이어의 업데이트·진도 저장 구현을 대신하는 화면이 아니다.

```powershell
cargo test --locked --test nested_repository_course --test repository_review_modes
node tools/verify-player-pilot.cjs
```

검증 결과와 화면은 `target/player-pilot-audit`에 저장된다. Node.js가 실제 실행기에 필요하다. 이 예제에는 해설이 없으며, 이후 해설·Git·선택형 티켓에서 같은 코스·수업을 확장한다. 정식 콘텐츠 변경에 필요한 해설 재생성 절차를 합성 예제에 성공한 것처럼 기록하지 않는다.

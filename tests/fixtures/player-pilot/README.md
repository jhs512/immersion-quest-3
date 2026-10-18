# 고정된 플레이어 검증 코스·수업

이 폴더는 정식 수업이 아닌 합성 테스트 데이터다. 코스·수업의 UUID는 스냅샷 간 유지하고, 스냅샷 A는 두 스텝, B는 기존 두 스텝과 추가된 한 스텝을 가진다. 실제 계정·외부 GitHub에는 요청하지 않는다. 실제 플레이어와 동일한 코스 불러오기·수업 열기·실행·채점·진도 처리 경로를 사용하고, 전송부만 메모리의 가상 GitHub 응답으로 대체한다. 지원하지 않는 요청은 외부로 넘기지 않고 거절한다.

새 형식은 계층이 스텝의 순서와 교육 목표를 소유하고, 같은 고유 코드로 문제 실행 데이터를 참조한다. 빠진 연결·중복·순서 불일치는 허용하지 않는다. 설명 목록에 챕터라는 이름만 붙이는 방식이 아니다. 코스의 해시는 정확한 UTF-8/LF 수업 바이트에 고정한다.

데이터는 프로세스별 임시 검증 폴더로 분리되며 실제 답안 저장소를 사용하지 않는다. Windows PowerShell에서 개발 빌드를 실행한다:

```powershell
cargo build --locked --bin molip-quest
$env:MOLIP_PILOT='1'
$env:WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS='--remote-debugging-port=9235'
$env:WEBVIEW2_USER_DATA_FOLDER=Join-Path (Get-Location) 'target/pilot-webview-profile'
& ./target/debug/molip-quest.exe
```

macOS에서는 개발 빌드에 `MOLIP_PILOT=1`을 전달해 같은 예제를 연다. UI 자동화 스크립트의 CDP 연결은 Windows WebView2 검증용이다. macOS 실제 화면 검증을 대신한다고 보고하지 않는다.

버전 a/b/c 버튼으로 스냅샷을 전환하고 초기화로 현재 문제 준비 코드를 복구한다. 손상 후보 버튼은 핀 해시와 맞지 않는 후보를 같은 로더에 넣어 거절을 확인하며 현재 스냅샷과 답안을 변경하지 않는다. C는 기존 한 문제를 활성 목록에서 빼고 다른 고유 코드의 문제를 추가한 교체 사례다. 교체 이유와 이전/새 코드는 별도 기대값에 보존한다. 이후 진도 전환 구현의 기준으로 사용한다. 실제 사용자 업데이트 UI 구현을 대신하는 것은 아니다.

```powershell
cargo test --locked --test nested_repository_course --test repository_review_modes
node tools/verify-player-pilot.cjs
```

검증 결과와 화면은 `target/player-pilot-audit`에 저장된다. Node.js가 실제 실행기에 필요하다. 이 예제에는 해설이 없으며, 이후 해설·Git·선택형 티켓에서 같은 코스·수업을 확장한다. 정식 콘텐츠 변경에 필요한 해설 재생성 절차를 합성 예제에 성공한 것처럼 기록하지 않는다.

D는 선택·배열·빈칸을 같은 실제 플레이어에서 제출하는 합성 예제다. E는 A의 필수 스텝 ID를 유지한 제목·표현 개정이며, 목록에서도 완료가 유지되는지 확인한다. `MOLIP_PILOT_SELF_TEST=1`로 실행하면 플랫폼의 네이티브 WebView에서 자동 검사하고 `target/pilot-native-result.json`을 쓴 뒤 종료한다. 검증 모드의 앱 업데이트는 합성 안내만 제공하고 실제 다운로드·교체를 차단한다.


F는 지연 Node 실행 중 해설 중단·학생 입력/답안 복원·열람 전후 이력을 검사한다. G는 아직 성공 기록이 없는 새 스텝을 추가한 실제 콘텐츠 업데이트 후보다. 버전 버튼은 검증 기준 상태를 다시 설치하며, '새 업데이트 공개'는 원격 후보만 바꾼다. 손상 업데이트 공개→수동 확인→거절→정상 후보 공개→사용자 적용→기존 답안/진도·새 미완료 스텝·백업 답안 복구까지 실제 업데이트 UI로 검사한다. 정식 과정이나 실제 GitHub 저장소를 바꾸지 않는다.

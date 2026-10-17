# 앱 안에서 gh 준비하기

gh를 찾지 못하거나 로그인하지 않은 경우 중앙 준비 화면을 보여 줘요. 앱 안의 실제 터미널에서 설치·로그인·상태 확인을 진행할 수 있어요. 이미 연결된 계정은 그대로 사용해요.

Windows의 ‘gh 설치’는 WinGet으로 공식 GitHub CLI를 설치해요. ‘GitHub 로그인’은 브라우저 승인 방식으로 진행해요. 질문과 Enter 입력은 내장 터미널에서 처리해요. 승인을 마치면 ‘준비 완료 · 연결 확인’을 눌러 과정으로 이동하세요.

새로 설치한 gh의 기본 설치 경로도 찾아요. 설치 때문에 앱을 재시작할 필요는 없어요. 터미널은 준비 화면을 떠날 때 종료되고, 앱은 터미널 출력 로그 파일을 만들지 않아요. 인증 정보는 기존처럼 gh가 관리해요.

터미널은 xterm.js와 운영체제의 PTY를 연결해요. 웹에서 명령 실행을 흉내 내는 화면이 아니에요. Android의 기존 열람 모드에는 데스크톱 터미널을 제공하지 않아요.

개발 빌드에서 `MOLIP_GH_SETUP_PREVIEW=1`로 실행하면 현재 계정을 로그아웃시키지 않고 준비 화면을 확인할 수 있어요. 이 설정은 첫 화면에만 적용돼요. 연결 확인 버튼은 실제 계정을 확인해요.

참고: [GitHub CLI Windows 설치](https://github.com/cli/cli/blob/trunk/docs/install_windows.md), [GitHub CLI 브라우저 로그인](https://cli.github.com/manual/gh_auth_login), [xterm.js](https://xtermjs.org/docs/), [portable-pty](https://docs.rs/portable-pty/0.9.0/portable_pty/).

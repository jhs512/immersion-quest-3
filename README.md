# MQ

## Windows · x64

1. [Windows 설치 파일](https://github.com/jhs512/immersion-quest-3/releases/latest/download/molip-quest-3-windows-x64-setup.exe)을 받으세요.
2. 다운로드한 파일을 실행해 설치하세요.
3. 시작 메뉴에서 **MQ**를 여세요. 이전 앱이 실행 중이면 종료한 뒤 다시 여세요.
4. 앱의 **gh 설치 → GitHub 로그인 → 준비 완료 · 연결 확인**을 순서대로 누르세요. 이미 로그인했다면 연결 확인만 누르면 돼요.

첫 실행 시 앱이 Java·C·Python을 진단하고 필요한 도구를 자동으로 준비해요. 정상인 기존 환경은 유지해요. 설치 결과는 **앱 설정 → 환경 진단**에서 확인하고, 실패한 경우 **환경 설치**로 다시 시도하세요.

## macOS · Apple Silicon / Intel · 12 이상

### 터미널로 설치

터미널에서 아래 명령을 실행하면 CPU에 맞는 앱을 설치하고 Java·C·Python 환경을 준비한 뒤 **MQ**를 열어요.

```bash
curl -fsSL https://raw.githubusercontent.com/jhs512/immersion-quest-3/main/packaging/macos/install.sh | bash
```

앱에서 **gh 설치 → GitHub 로그인 → 준비 완료 · 연결 확인**을 누르세요.

Java는 CPU를 자동으로 구분해 앱 전용 JDK 25를 준비해요. macOS의 C 도구 설치 창이 나오면 **설치**와 **약관 확인**을 완료하세요. 앱에서 **환경 진단**으로 완료 여부를 확인할 수 있어요.

### 설치 파일로 설치

1. CPU에 맞는 파일을 받으세요: [Apple Silicon(M1 이후)](https://github.com/jhs512/immersion-quest-3/releases/latest/download/molip-quest-3-macos-arm64.dmg) / [Intel Mac](https://github.com/jhs512/immersion-quest-3/releases/latest/download/molip-quest-3-macos-x86_64.dmg).
2. 실행 중인 MQ를 종료하세요. DMG 안의 **MQ.app**을 **응용 프로그램(Applications)**으로 옮기고 기존 앱을 교체하세요.
3. 응용 프로그램의 **MQ**를 열고 위의 GitHub 연결과 실행 환경 준비를 진행하세요. 첫 실행 시 필요한 환경을 자동으로 준비해요. 설치 결과는 **앱 설정 → 환경 진단**에서 확인하세요.

첫 실행이 차단되면 **시스템 설정 → 개인정보 보호 및 보안 → 그래도 열기**를 선택하세요.

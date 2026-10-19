# 몰입 퀘스트 3

## Windows · x64

1. [Windows 설치 파일](https://github.com/jhs512/immersion-quest-3/releases/latest/download/molip-quest-3-windows-x64-setup.exe)을 받으세요.
2. 다운로드한 파일을 실행해 설치하세요.
3. 시작 메뉴에서 **몰입 퀘스트 3**를 여세요.
4. 앱의 **gh 설치 → GitHub 로그인 → 준비 완료 · 연결 확인**을 순서대로 누르세요. 이미 로그인했다면 연결 확인만 누르면 돼요.

필요한 실행 환경은 수업에 맞춰 준비하세요.

- **Java**: [JDK 25](https://adoptium.net/temurin/releases/?version=25)를 설치한 뒤 앱을 다시 여세요.
- **Python**: 앱의 **환경 설치**로 준비하고 **환경 진단**에서 확인하세요.

## macOS · Apple Silicon

### 터미널로 설치

터미널을 열고 아래 명령을 붙여 넣으세요. Apple Silicon용 앱과 Python 실행 환경을 설치한 뒤 앱을 열어요.

```bash
curl -fsSL https://raw.githubusercontent.com/jhs512/immersion-quest-3/main/packaging/macos/install.sh | bash
```

앱에서 **gh 설치 → GitHub 로그인 → 준비 완료 · 연결 확인**을 누르세요. `gh 설치`에 필요한 Homebrew가 없다면 [Homebrew 설치 안내](https://brew.sh/ko/)를 먼저 따라 주세요.

필요한 실행 환경은 수업에 맞춰 준비하세요.

- **Java**: [JDK 25](https://adoptium.net/temurin/releases/?version=25)를 설치한 뒤 앱을 다시 여세요.
- **C**: 터미널에서 `xcode-select --install`을 실행하세요.
- **Python**: 위 설치 명령이 함께 준비해요. 앱의 **환경 진단**에서 확인하세요.

### 설치 파일로 설치

1. [Apple Silicon(M1 이후)용 DMG](https://github.com/jhs512/immersion-quest-3/releases/latest/download/molip-quest-3-macos-arm64.dmg)를 받으세요.
2. DMG를 열고 **몰입 퀘스트 3.app**을 **응용 프로그램(Applications)**으로 옮기세요.
3. 앱을 열고 위의 GitHub 연결과 실행 환경 준비를 진행하세요. Python 환경은 앱의 **환경 설치**로 준비할 수 있어요.

첫 실행이 차단되면 **시스템 설정 → 개인정보 보호 및 보안 → 그래도 열기**를 선택하세요.

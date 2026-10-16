# OmniRoute 조사

확인일: 2026-10-03. 설치와 실제 호출 검증은 별도 작업이다. 이 문서는 공식 문서·소스와 배포 목록을 조사한 결과이며 앱 코드는 변경하지 않았다.

## 무엇을 하는 프로그램인가

OmniRoute는 여러 AI 공급자를 하나의 로컬 API로 연결하는 게이트웨이다. 사용 도구가 요청하면 선택한 공급자로 보내고, 설정에 따라 다른 모델로 넘어간다. 자체가 오프라인 언어 모델은 아니다. 최신 정식 버전 README에는 OpenCode Free 무인증 경로가 기본 `auto`에 연결된다고 나와 있다. 따라서 시작부터 외부 서비스 가입이 반드시 필요한 것은 아니다. 무료 공급자의 실제 가용성은 실행 시 확인해야 한다. [정식 버전 README](https://github.com/diegosouzapw/OmniRoute/blob/v3.8.51/README.md)

설치 복구에서 파일을 바꾸고 명령을 실행하는 역할은 Claude Code/Codex 같은 에이전트가 맡는다. OmniRoute는 그 에이전트가 사용할 모델 연결을 담당한다. `omniroute run claude` 또는 `omniroute run codex`는 별도 CLI를 올바른 연결 환경으로 실행한다. 에이전트 설치 여부도 따로 진단해야 한다. [CLI 연결 안내](https://github.com/diegosouzapw/OmniRoute/blob/v3.8.51/docs/guides/CLI-INTEGRATIONS.md)

## Windows 설치

조사 당시 GitHub 최신 정식 릴리즈는 **v3.8.51**이다. 기본 브랜치는 `release/v3.8.52`로, 브랜치 문서와 설치한 정식 버전을 혼동하면 안 된다. 정식 릴리즈에는 Windows 설치형 `OmniRoute.Setup.3.8.51.exe`와 휴대형 `OmniRoute.3.8.51.exe`가 실제로 첨부되어 있다. [정식 릴리즈](https://github.com/diegosouzapw/OmniRoute/releases/tag/v3.8.51)

터미널 설치 경로는 다음과 같다.

```powershell
npm install -g omniroute
omniroute
```

npm 경로에는 Node/npm이 필요하다. v3.8.51 패키지의 Node 범위는 `>=22.22.2 <23 || >=24.0.0 <27`이다. 현재 컴퓨터의 Node 24.13.1은 부모 작업에서 확인한 값으로 이 범위를 만족한다. Windows 데이터는 기존 `%USERPROFILE%\.omniroute`가 없으면 `%APPDATA%\omniroute`를 사용한다. `DATA_DIR`로 변경 가능하다. [설치 가이드](https://github.com/diegosouzapw/OmniRoute/blob/v3.8.51/docs/guides/SETUP_GUIDE.md), [패키지 요구조건](https://github.com/diegosouzapw/OmniRoute/blob/v3.8.51/package.json)

Electron 설치형은 자체 Node 런타임으로 서버를 실행하므로, npm 방식과 달리 시스템 Node를 따로 관리하지 않아도 되는 경로다. [데스크톱 구조](https://github.com/diegosouzapw/OmniRoute/blob/v3.8.51/docs/guides/ELECTRON_GUIDE.md)

## 가입·로그인 안내를 어떻게 나눌까

OmniRoute의 로컬 관리 화면 인증, AI 공급자의 인증, Claude/Codex CLI 인증은 다른 상태다. 하나의 ‘로그인됨’ 표시로 합치지 않는다.

| 선택 경로 | 필요한 준비 |
|---|---|
| OpenCode Free | 공급자 API 키나 가입 없이 시작 가능한 경로 |
| Gemini / Google AI Studio | Google 계정으로 접속하고 API 키 생성 |
| Groq | Groq Console 계정 및 API 키 준비 |
| OpenRouter | OpenRouter 계정 및 API 키 준비 |
| Claude Code / Codex 공급자 | 해당 계정의 OAuth 연결과 이용 가능한 계정·요금제 확인 |
| 로컬 Ollama | 모델을 로컬에 준비하고 Ollama 실행; 로컬 연결 자체에는 API 키 불필요 |

이 중 **사용자가 선택한 경로만 준비하도록** 안내한다. 학생 모두에게 여러 서비스 가입을 강요하지 않는다. 공급자 목록의 ‘No-auth’에는 Codex app-server처럼 자체 키를 저장하지 않지만 원래 CLI의 로그인이 필요한 항목도 있으므로 이름만으로 완전 무인증이라고 판정하면 안 된다. [공급자별 인증 표](https://github.com/diegosouzapw/OmniRoute/blob/v3.8.51/docs/reference/PROVIDER_REFERENCE.md)

대표 서비스의 키 발급·연결은 각 서비스 문서를 따라간다. [Google API 키](https://ai.google.dev/gemini-api/docs/api-key), [Groq 시작 안내](https://console.groq.com/docs/quickstart), [OpenRouter 시작 안내](https://openrouter.ai/docs/quickstart), [Ollama 시작 안내](https://docs.ollama.com/quickstart)

## 닥터에서 확인할 항목

1. 설치된 OmniRoute 버전과 실행 파일 위치.
2. 기본 로컬 주소 `http://127.0.0.1:20128`의 서버 가동 상태. 포트를 변경한 기존 설치도 존중한다.
3. `GET /api/health`는 프로세스 가동 여부, `GET /api/health/ping`는 DB 응답까지 확인한다. 두 경로는 정식 버전 소스에서 무인증임을 확인했다. [가동 확인 소스](https://github.com/diegosouzapw/OmniRoute/blob/v3.8.51/src/app/api/health/route.ts), [DB 준비 확인 소스](https://github.com/diegosouzapw/OmniRoute/blob/v3.8.51/src/app/api/health/ping/route.ts)
4. `omniroute doctor`로 설정, DB, 포트, Node, 네이티브 의존성 등의 로컬 진단. 출력 옵션은 설치 버전의 `--help`로 확인한다. 문서는 JSON 출력을 안내하지만 소스는 공통 출력 옵션도 사용하므로 문자열을 고정하지 않는다. [doctor 소스](https://github.com/diegosouzapw/OmniRoute/blob/v3.8.51/bin/cli/commands/doctor.mjs)
5. `GET /v1/models`로 모델 목록을 읽고, 짧은 실제 요청까지 수행해 공급자 사용 가능 여부를 확인한다. 목록만으로 로그인·요금제·잔여량·도구 호출 호환성이 검증되지는 않는다. [API 명세](https://github.com/diegosouzapw/OmniRoute/blob/v3.8.51/docs/reference/API_REFERENCE.md)

## 몰입 퀘스트 연결 제안

- OmniRoute가 준비됐으면 모델 연결에 우선 사용한다. 실행 에이전트 선택은 Claude 기본값, Codex 선택 가능으로 유지한다. 둘은 경쟁 선택지가 아니라 게이트웨이와 실행 도구의 조합이다.
- 설명·힌트는 게이트웨이 API에 직접 요청할 수 있다. 설치 복구는 선택된 CLI 에이전트가 실행하고 결과를 닥터가 재검사하는 방식으로 구성한다.
- `omniroute run`은 사용자 기본 설정을 쓰지 않고 실행 환경을 주입하는 경로다. 앱 전용 실행에는 사용자 전체 CLI 설정을 덮어쓰는 것보다 이 방식을 먼저 검토한다. [CLI 실행 계약](https://github.com/diegosouzapw/OmniRoute/blob/v3.8.51/docs/guides/CLI-INTEGRATIONS.md)
- 직접 연결할 경우 Claude Code는 `ANTHROPIC_BASE_URL`에 `/v1`을 붙이지 않는다. Codex 연결은 TOML 프로파일과 OpenAI 호환 Responses API 설정을 사용한다. 실제 설치 버전에서 비대화형 실행·도구 호출까지 검사해야 한다. [Claude 설정](https://github.com/diegosouzapw/OmniRoute/blob/v3.8.51/docs/guides/CLAUDE-CODE-CONFIGURATION.md), [Codex 설정](https://github.com/diegosouzapw/OmniRoute/blob/v3.8.51/docs/guides/CODEX-CLI-CONFIGURATION.md)
- 사용자와 확정한 최대 10회 복구, 실패 원인 표시, 다시 시도 버튼은 몰입 퀘스트에서 구현할 정책이다. OmniRoute가 이 정책을 자동으로 제공한다고 가정하지 않는다.
- 기본 수업·코드 실행은 오프라인으로 유지한다. 외부 AI 연결과 설치 다운로드에는 인터넷이 필요하다. 로컬 Ollama 선택만으로 충분한 복구 품질까지 보장되지는 않는다.

## Windows 실제 시험 — 2026-10-03

- Windows-MCP로 보이는 CMD에서 Node 24.13.1 확인, `npm install -g omniroute` 완료(3.8.51).
- `omniroute` 실행 후 관리 화면 접속 및 초기 로그인 완료. 서버는 127.0.0.1로 제한했고 사용자 설정 파일에도 저장했다.
- Claude 설정 파일은 바꾸지 않았다. 시험 프로세스에서만 ANTHROPIC_BASE_URL과 모델을 변경했다.

| 경로 | 시험 | 실제 결과 |
|---|---|---|
| OpenCode Free / Big Pickle | 관리 화면 모델 시험, 일반 API 질문 | 상류 403: OpenCode 안에서만 무료 사용 가능. 후속 연결정보 오류는 무료 경로 일시 중단의 결과였다. |
| OpenCode Free / DeepSeek, MiMo | 추가 모델 요청 | 무료 경로가 중단돼 응답 실패. 모델 성능 평가 불가. |
| DuckDuckGo / Claude Haiku | 짧은 API 인사 | 실제 답변 수신. |
| DuckDuckGo / Claude Haiku | Claude Code, 도구 없는 짧은 인사 | CLI 기본 입력이 길어 ERR_INPUT_LIMIT. 재시도 종료. |
| DuckDuckGo / GPT Mini | 코드 요청 | 앞선 실패로 circuit breaker가 열려 503. 모델 성능 평가 불가. |
| Cloudflare Playground / Llama 3.1 8B | 짧은 API 인사 | 응답 수신, 일반 인사 대신 JSON 형태의 문자열 반환. |
| Cloudflare Playground / Qwen2.5 Coder 32B | Claude Code, 도구 없이 add 함수 작성 | 코드 답변 수신, CLI 종료 코드 0. |
| Cloudflare Playground / Qwen2.5 Coder 32B | Claude Code Read로 probe.txt 읽기 | 실제 파일 내용을 못 가져옴. 도구 호출 검증 실패. |
| Cloudflare Playground / GLM 5.2 | 같은 Read 시험 | 읽겠다는 말만 반환, 실제 파일 내용 없음. 도구 호출 검증 실패. |

### 해석

OmniRoute 설치와 모델 텍스트 응답은 확인됐다. 무료 연결 중 Cloudflare 경로는 Claude Code의 코드 답변까지 됐지만, 도구 호출은 확인되지 않았다. 이 결과로 설치 자동 복구에 사용할 수 있다고 판단하면 안 된다. OpenCode 무료의 클라이언트 제한을 우회하지 않았다. 선택한 서비스의 정식 API/OAuth 연결을 다음 후보로 검증해야 한다. 모델 목록이나 연결됨 표시는 실제 응답/도구 성공을 보장하지 않는다.

## 무료 연결 추가 조사 — 2026-10-03

### 다음 시험 후보

**NVIDIA NIM의 Nemotron 3 Super를 먼저 시험한다.** 공식 모델 페이지에 무료 엔드포인트가 현재 사용 가능하고, 코딩·도구 호출을 지원한다고 명시되어 있다. NVIDIA 계정으로 Developer Program에 가입·로그인한 뒤 API 키를 만들고 OmniRoute의 NVIDIA 공급자에 연결하는 경로다. 호스팅 API이므로 학생 컴퓨터에 NVIDIA GPU를 설치할 필요는 없다. 무료 범위는 프로토타이핑이며 무제한 운영 서비스를 보장하지 않는다. [현재 모델과 무료 엔드포인트](https://build.nvidia.com/nvidia/nemotron-3-super-120b-a12b), [키 발급 절차](https://docs.api.nvidia.com/nim/docs/api-quickstart), [무료 사용 목적](https://docs.api.nvidia.com/nim/docs/run-anywhere)

모델의 도구 호출 지원과 **OmniRoute → Claude Code에서 실제 파일 도구가 작동하는 것**은 별개다. 아래 후보들은 이번 추가 조사에서 새로 실행하지 않았다. 먼저 위의 실제 시험처럼 임의 내용을 가진 파일 읽기를 검증하고, 이어 파일 수정 및 간단한 Python 실행을 검증해야 한다. 모델이 실행했다고 말하는 것만으로 통과 처리하지 않는다.

### 요청한 여섯 경로 대조

| 후보 | 가입·인증 및 무료 조건 | 도구 호출·연결 판단 |
|---|---|---|
| NVIDIA NIM | NVIDIA 계정·Developer Program·API 키. 공식 무료 프로토타입 엔드포인트를 이용. 현재 일일·월간 고정 한도나 무제한 보장은 확인하지 못함. | Nemotron 3 Super 공식 페이지가 코딩·tool calling과 Free Endpoint Available을 명시. OmniRoute NVIDIA API 키 경로의 첫 시험 후보. |
| Google AI Studio / Gemini API | Google 계정·API 키. 일부 모델에 무료 티어가 있고 모델·프로젝트별 한도는 AI Studio에서 확인. | 공식 function calling 지원. 정식 API 키 경로로 시험할 수 있음. Antigravity OAuth와 다른 경로. |
| OpenRouter 무료 모델 | OpenRouter 계정·API 키. 현재 공식 가격표의 무료 플랜은 하루 50 요청. 무료 모델 목록과 공급자별 추가 제한은 바뀔 수 있음. | tools 지원 무료 모델을 골라 시험. 예: 공식 Qwen 무료 모델 API 페이지에 tools/tool_choice가 표시됨. 짧은 검증에는 적합하지만 10회 복구 과정이 여러 요청을 소비할 수 있음. |
| Groq 무료 플랜 | Groq Console 계정·API 키. 현재 gpt-oss-120b/20b 표는 분당 30 요청·하루 1,000 요청·분당 8,000 토큰·하루 200,000 토큰. 조직 단위 제한이며 실제 계정 Limits도 확인. | 공식 표는 두 gpt-oss 모델의 도구 호출 지원을 명시하지만 병렬 도구 호출은 미지원. Claude Code의 긴 초기 입력이 분당 토큰 한도에 걸릴 수 있어 보조 후보. |
| Kiro 무료 OAuth | 기본 무료 플랜은 월 50 크레딧. Kiro 원래 인터페이스를 위한 무료 제공. | 공식 FAQ가 원래 인터페이스 밖의 제삼자 harness로 요청을 라우팅하는 사용을 금지. OmniRoute를 통한 Claude Code 무료 연결 후보에서 제외. |
| Antigravity OAuth | Antigravity 자체 계정·이용 조건에 따른 제공. | 공식 약관 6항이 제삼자 도구를 통한 서비스 접근 및 OAuth 재사용을 명시적으로 제한. 이 OAuth를 OmniRoute에 연결하는 후보에서 제외. |

근거: [NVIDIA 모델](https://build.nvidia.com/nvidia/nemotron-3-super-120b-a12b), [Gemini 가격](https://ai.google.dev/gemini-api/docs/pricing), [Gemini 한도](https://ai.google.dev/gemini-api/docs/rate-limits), [Gemini 도구 호출](https://ai.google.dev/gemini-api/docs/function-calling), [OpenRouter 가격](https://openrouter.ai/pricing/), [OpenRouter Qwen 무료 API](https://openrouter.ai/qwen/qwen3.8-27b%3Afree/api), [Groq 한도](https://console.groq.com/docs/rate-limits), [Groq 도구 지원](https://console.groq.com/docs/tool-use/overview), [Kiro 가격·FAQ](https://kiro.dev/pricing/), [Antigravity 약관](https://antigravity.google/terms).

OmniRoute v3.8.51 공급자 문서에 NVIDIA·Groq·Gemini·OpenRouter API 키 연결이 나와 있다. 다만 그 문서의 무료 요청 수가 현재 공급자 가격표와 다를 때에는 공급자의 현재 안내를 우선한다. 예를 들어 OpenRouter의 과거 200 RPD 안내를 지금의 무료 플랜 한도로 그대로 사용하면 안 된다. [OmniRoute 공급자 표](https://github.com/diegosouzapw/OmniRoute/blob/v3.8.51/docs/reference/PROVIDER_REFERENCE.md), [무료 티어 문서의 변동성 안내](https://github.com/diegosouzapw/OmniRoute/blob/v3.8.51/docs/reference/FREE_TIERS.md)

또한 NVIDIA 모델마다 무료 엔드포인트 상태가 다르다. Qwen3 Coder 480B 페이지는 현재 Free Endpoint Deprecated이므로 오래된 영상에 나온 이름을 그대로 추천하지 않는다. [Qwen3 Coder 상태](https://build.nvidia.com/qwen/qwen3-coder-480b-a35b-instruct)

### 영상·블로그·Hacker News에서 실제 확인한 범위

- 부모 작업에서 Geeky Beginners 작성자의 블로그 본문을 직접 확인했다. Claude Code Desktop과 OmniRoute 연결 및 Kiro·Antigravity 사용을 소개하지만, 현재 공식 이용 조건과는 별도로 판단한다. 연결된 영상의 전체 재생은 확인하지 않았다. [작성자 블로그](https://www.geekybeginners.com/how-to-use-free-ai-providers-in-claude-code-desktop-with-omniroute/)
- Amidia 영상의 공개 Glasp 요약과 자막 발췌는 확인했다. NVIDIA API 키 연결과 모델별 성공·실패 시험이 소개되지만 전체 자막은 접근 오류로 읽지 못했다. 이는 후보 발견용 자료이며 무료 한도나 도구 호출 성공의 공식 근거가 아니다. [영상 공개 요약·자막 발췌](https://glasp.co/youtube/NJ0TQ-pyMDY)

- YouTube의 **I Gave CLAUDE CODE 1.6 Billion Free Tokens Every Day** 원본 페이지와 제목을 찾았다. 이 조사 도구로 영상의 전체 자막이나 실제 재생 내용을 확인하지 못했다. 제목의 토큰 수를 개인에게 보장된 매일 무료 한도로 인용하지 않는다. 여러 공급자 무료량 합계와 한 계정의 실제 사용 한도는 다르다. [영상 원본](https://www.youtube.com/watch?v=NJ0TQ-pyMDY)
- Aditi Gupta의 OmniRoute 설치·Claude Code·Docker·문제 해결 블로그 원본 및 연결된 GoVenture-Live 영상이 검색 결과에 나타났다. 블로그 전체 본문은 접근 오류 때문에 검증하지 못했으므로 설치 성공이나 현재 무료 호환성의 증거로 사용하지 않는다. [블로그 원본](https://honestaireview.hashnode.dev/omniroute-ai-installation-claude-code-docker-and-troubleshooting), [연결된 영상](https://www.youtube.com/watch?v=JbrM6S5l3Io)
- HN에는 작성자 AliShahryar가 올린 **Show HN: Free Unlimited Claude Code Usage with Nvidia Nim Models**가 실제 존재한다. 작성자는 NIM 연결 프록시로 tool calling을 유지했다고 주장한다. 현재 연결 저장소의 기본 모델은 Nemotron 3 Super다. 이는 다음 시험 후보를 고르는 단서이며, 우리의 OmniRoute 환경에서 검증됐다는 뜻은 아니다. 확인한 HN 페이지에 사용자들의 독립적인 성공 검증 댓글은 표시되지 않았다. [HN 원문](https://news.ycombinator.com/item?id=46917761), [작성자의 구현](https://github.com/Alishahryar1/free-claude-code)
- HN 검색에서 OmniRoute를 로컬 게이트웨이로 쓴다는 실제 댓글 하나도 확인했다. 이것만으로 널리 검증된 무료 조합이나 커뮤니티 합의가 있다고 말하지 않는다. [HN 댓글 데이터](https://hn.algolia.com/api/v1/items/48999634)

NVIDIA 40 RPM은 OmniRoute 문서와 위 작성자 주장에 나오지만 현재 NVIDIA 공식 무료 제공 문서의 보장 수치로 확인하지 못했다. ‘무료 무제한’이라는 표현 대신 계정의 실제 한도와 응답을 확인한다. 키를 발급받아야 하는 단계에서는 사용자가 선택한 서비스 한 곳만 준비하고, 결제나 제한 회피 없이 정식 제공 범위에서 시험한다.

### 몰입 퀘스트 설치 닥터에 반영할 안내

기본 안내는 ‘NVIDIA 계정으로 로그인하고 무료 프로토타입 API 키를 생성’으로 시작할 수 있다. 다음 선택지는 Gemini API, OpenRouter 무료 모델, Groq로 두되, 모두 가입할 필요는 없다고 표시한다. 설치 닥터는 공급자 연결, 실제 텍스트 요청, 파일 읽기, 파일 변경·실행을 별도 상태로 보여준다. 무료 연결의 텍스트 답변만 성공한 상태는 설치 자동 복구 준비 완료로 표시하지 않는다. 기본 수업과 Python 실습의 오프라인·무회원 흐름은 그대로 유지한다.

## NVIDIA NIM 실제 연결 시험 — 2026-10-03
- NVIDIA 계정 인증 후 API 키 발급, OmniRoute NVIDIA 공급자 키 검증 성공. 무료 모델만 가져오기 설정 사용.
- OmniRoute 로컬 호출 키를 생성하고 인증된 모델 목록 조회 성공. 키와 개인정보는 이 문서에 기록하지 않음.
- 모델: nvidia/nemotron-3-super-120b-a12b. Claude Code 요청은 OmniRoute 모델 접두사를 포함하여 전달.
- Claude Code Read 실제 호출로 probe.txt 내용 확인 성공.
- Claude Code Write 실제 호출로 nvidia_probe.py 생성 성공. 파일 내용도 별도로 확인.
- Claude Code Bash 실제 호출: 파일 목록 확인, 작성 파일 확인, python nvidia_probe.py 실행. 실제 stdout 5 확인.
- 실행 시험은 세 번의 도구 호출 뒤 최종 답변 전에 max-turns=3 제한에 걸려 CLI 종료 코드는 1. 실행 자체는 도구 결과로 성공 확인됨.
- 결론: 이전 무료 공급자 시험과 달리 NVIDIA 경로는 실제 파일 읽기·쓰기·명령 실행까지 확인. 설치 자동 복구 전체나 장기 안정성은 아직 검증하지 않음. 공급자 간 폴백도 아직 설정·검증하지 않음.
- Claude Code의 costUSD 값은 알 수 없는 모델에 대한 내부 추정치이며 NVIDIA 실제 청구 증거로 해석하지 않음.

## OmniRoute 사용자 공급자 선택 조사 — 2026-10-03
공개 사용 사례는 여러 공급자를 함께 구성하는 방식이 확인되지만, NVIDIA와 OpenRouter의 실제 사용 점유율/순위를 확인할 공개 통계는 찾지 못했다. 제작자 홍보글의 반복 게시를 독립 사용자 사례 수로 세지 않았다.
- 직접 사용자 GitHub 요청: OpenRouter, Groq, Gemini, Cerebras, NVIDIA NIM 등 여러 무료 API를 연결하고 자동 combo에 포함되길 요청. https://github.com/diegosouzapw/OmniRoute/issues/7563
- 직접 사용자 오류 보고: OpenRouter와 NVIDIA 모두 연결한 상태에서 모델 기능 표시 문제 보고. https://github.com/diegosouzapw/OmniRoute/issues/4264
- 직접 사용자 Reddit 사용기: OpenRouter 무료 모델을 쓰고 NVIDIA NIM을 다른 연결이 소진됐을 때 대체로 배치. 개별 사용자 사례이며 대표성은 불명. https://www.reddit.com/r/opencodeCLI/comments/1vu7bkp/rip_deeepseekv4flash_omnirouter_is_my_new_best/
결론: 두 서비스는 택일보다 함께 쓰는 공개 사례가 있다. 우리 환경은 NVIDIA 도구 실행을 직접 검증했으므로 이를 출발점으로 삼을 근거가 있으며, 이는 인기 순위 판단과 별개다.

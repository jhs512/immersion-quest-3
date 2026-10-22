# 몰입 퀘스트 3 릴리즈

MQ3 전용 소스·릴리즈 저장소는 [jhs512/immersion-quest-3](https://github.com/jhs512/immersion-quest-3)예요. 원본 jhs512/molip-quest와 별개예요. 현재 소스와 릴리즈 저장소는 공개예요. 공개 코스·수업 저장소는 그대로예요.

main에 푸시하면 Windows x64 설치 프로그램과 macOS Apple Silicon·Intel DMG를 만들어요. 설치와 제거가 성공하고 설치 파일 검사까지 통과해야 릴리즈를 게시해요. 새 푸시는 이전 실행을 취소해요. 빌드 작업은 읽기 권한만 갖고, 릴리즈 작업만 콘텐츠 쓰기 권한을 받아요.

릴리즈 태그는 v<앱 버전>-build.<워크플로 실행 번호>예요. 설치 프로그램과 SHA256SUMS를 먼저 초안에 올린 뒤 완성된 릴리즈로 전환해요. Windows 설치와 앱 업데이트 모두 이 저장소만 사용해요. Mac 최초 설치는 [터미널 설치 안내](../README.md#macos--apple-silicon--12-이상)를 따라요. DMG 직접 다운로드를 설치 방법으로 안내하지 않아요.

공개 릴리즈는 누구나 받을 수 있어요. 학습 진도에는 기존 gh 로그인을 사용해요. 앱 업데이트도 같은 저장소에서 받아요. 토큰을 앱이나 워크플로 파일에 넣지 않아요.

설치 이름은 ‘몰입 퀘스트 3’, 경로는 %LOCALAPPDATA%\\Programs\\MolipQuest3예요. 원본 앱과 설치 식별자가 달라요. 자동 업데이트는 이 MQ3 설치를 덮어써요. 기존 로컬 학습 데이터 위치는 변경하지 않아요.

자동 배포 대상은 Windows x64와 macOS arm64·x64예요. macOS 작업은 각 아키텍처의 네이티브 러너에서 컴파일, PTY·업데이트 검사, 서명 무결성·DMG 검사와 앱 프로세스 시작을 확인해요. 실제 학생 계정 로그인과 음성 재생의 대화형 기기 검사는 별도예요. 모든 작업이 성공해야 함께 릴리즈해요. Android는 포함하지 않아요. Windows 인증서와 Apple Developer ID 공증은 아직 설정하지 않았어요. Mac 첫 실행은 packaging/macos/먼저 읽어 주세요.txt를 따라요.

개인 설정, .scratch, 로컬 문서, 빌드 출력, 가상 환경, 의존성 설치 폴더, 서명 키, 강사 전용 정답·암호화 자료는 소스에 올리지 않아요. 로컬의 강사 자료는 그대로 보존하며, 깨끗한 CI 빌드는 그 자료 없이 컴파일돼요. 일반 코스·공개 문제의 풀이와 해설은 유지해요.

설정 근거: [GitHub 워크플로 권한·동시 실행 문법](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax).

Mac 설치 이름은 몰입 퀘스트 3.app이에요. Finder에서 열어도 Homebrew와 사용자 도구 경로를 찾고, JDK 25는 macOS java_home으로 찾아요. 자동 업데이트는 실행 중인 Mac 아키텍처의 파일을 선택해요.

Intel Mac의 한 줄 설치는 Python 3.12·TensorFlow 2.16.2를 사용해요. TensorFlow 공식 Intel Mac 지원은 2.16에서 끝나므로 Apple Silicon과 같은 최신 버전을 강제하지 않아요. 근거: https://www.tensorflow.org/install/pip

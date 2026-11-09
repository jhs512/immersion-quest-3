# MQ의 기존 실습과 채점기 어디에 Floci를 연결할 수 있는가

조사일: 2026-11-09. 불변 기준: `jhs512/immersion-quest-3`의 `0d551472b3036ae6a0920e563d3ec5970f33ef8c` (`origin/main`에서 분기). 이 문서는 계획용 조사다. 첫 적용을 **기존 네트워크 보강**으로 할지 **후속 AWS 실습**으로 할지는 사용자의 답을 기다리는 중이며, 어느 쪽도 승인된 순서로 간주하지 않는다. 수업·실행기·정책을 수정하거나 빌드·Docker 실습·클라우드 자원 생성을 실행하지 않았다.

## 판단 요약

MQ에는 로컬 서비스 실습에 필요한 소유 자원 관리, 환경 복원, 해설 분리, 실제 상태 채점의 선례가 있다. 그러나 Floci를 현 콘텐츠의 이미지나 네트워크 종류에 추가하는 것만으로 연결되지는 않는다. 일반 Docker 실행기는 이미지 저장소를 네 종류로 제한하며, Java 라이브러리 실행기는 AWS SDK를 제공하지 않는다. 네트워크 채점기는 여덟 종류의 IP·경로·DNS 실습에 특화되어 있다. 따라서 재사용할 기반과 새로 설계할 AWS 상태 관찰자를 나누는 것이 조사상 타당하다. 이는 구현 승인이나 최종 설계 결정이 아니다. [이미지 제한](https://github.com/jhs512/immersion-quest-3/blob/0d551472b3036ae6a0920e563d3ec5970f33ef8c/src/docker_lab.rs#L75-L106), [Java 묶음 제한](https://github.com/jhs512/immersion-quest-3/blob/0d551472b3036ae6a0920e563d3ec5970f33ef8c/src/library_sets.rs#L1-L25), [네트워크 종류](https://github.com/jhs512/immersion-quest-3/blob/0d551472b3036ae6a0920e563d3ec5970f33ef8c/src/network_practice.rs#L11-L33).

## 현재 수업과 연결 후보

배포 기록은 기존 Java 48·AICE 24·정보처리기사 30수업을 유지하고 네트워크 8수업을 추가하여 생성 Java 코스가 56수업이라고 설명한다. 운영 Java 코스에는 별도 웹 수업이 있어 기존 50개가 유지될 때 게시 후 58수업이라는 조건부 계산이다. 이 조사에서 운영 원격 코스의 현재 수를 다시 조회한 것은 아니다. 제작 카탈로그 자체도 런타임 manifest나 제작 완료 선언이 아니라고 명시한다. [배포 기록](https://github.com/jhs512/immersion-quest-3/blob/0d551472b3036ae6a0920e563d3ec5970f33ef8c/docs/network-foundations-release.md#L1-L7), [카탈로그 성격](https://github.com/jhs512/immersion-quest-3/blob/0d551472b3036ae6a0920e563d3ec5970f33ef8c/tools/redesigned_courses/catalog.json#L1-L4).

새 네트워크 본편은 바이트 → 끝점 → IP → 라우팅 → DNS → TCP → UDP → HTTP의 8수업이다. Docker 이미지·컨테이너 도입 뒤에 놓이고 기존 Docker 네트워크 수업으로 이어진다. Java 실행 문제 32개와 별도로 IP 4개·라우팅 2개·DNS 2개의 실제 Docker 상태 실습이 연결된다. [카탈로그 순서](https://github.com/jhs512/immersion-quest-3/blob/0d551472b3036ae6a0920e563d3ec5970f33ef8c/tools/redesigned_courses/catalog.json#L946-L1136), [문제 구성](https://github.com/jhs512/immersion-quest-3/blob/0d551472b3036ae6a0920e563d3ec5970f33ef8c/docs/network-foundations-release.md#L9-L21).

아래는 선수 **후보**이며 진도 잠금 제안이 아니다. MQ의 코딩 문제는 자체 준비 자료를 갖추고 다른 문제의 실행 결과에 의존하지 않는 독립 실습이다. [도메인 정의](https://github.com/jhs512/immersion-quest-3/blob/0d551472b3036ae6a0920e563d3ec5970f33ef8c/CONTEXT.md#L88-L91).

| 후보 수업 | AWS 실습에서 가져올 지식 | 필요한 경우 |
| --- | --- | --- |
| Bash 기본, 변수, 환경 변수, 명령 한 번의 환경·인자 | 경로·환경 값·프로세스 인자 구별 | CLI를 학습 목표로 삼을 때. 준비된 SDK 코드 문제라면 전부 선수로 올리지 않는다. |
| Java 파일·예외, 검증·작은 테스트 | 파일 바이트와 오류, 실행 결과 확인 | Java SDK 문제에서 사용하는 부분만 |
| 이미지와 컨테이너 | 로컬 서비스 시작·정지·재생성의 의미 | 학생이 실행 환경도 조작할 때 |
| 네트워크 끝점·HTTP, Docker 네트워크 | PC와 컨테이너의 localhost, 주소·포트·요청 응답 | endpoint 변경 실패를 직접 관찰할 때 |

후보의 실제 존재와 목표는 [Bash·환경 수업](https://github.com/jhs512/immersion-quest-3/blob/0d551472b3036ae6a0920e563d3ec5970f33ef8c/tools/redesigned_courses/catalog.json#L61-L77), [변수·환경·인자](https://github.com/jhs512/immersion-quest-3/blob/0d551472b3036ae6a0920e563d3ec5970f33ef8c/tools/redesigned_courses/catalog.json#L352-L414), [파일·검증](https://github.com/jhs512/immersion-quest-3/blob/0d551472b3036ae6a0920e563d3ec5970f33ef8c/tools/redesigned_courses/catalog.json#L594-L702), [Docker·네트워크](https://github.com/jhs512/immersion-quest-3/blob/0d551472b3036ae6a0920e563d3ec5970f33ef8c/tools/redesigned_courses/catalog.json#L946-L1136)에 근거한다. 위 표의 교육적 연결은 조사자의 제안이다.

## 실행기에서 재사용할 것과 새로 필요한 것

| 영역 | 확인된 현재 동작 | Floci 연결에 대한 판단 |
| --- | --- | --- |
| 준비·재접속 | `network-state.json`에 종류·주소 기반·역할·준비 여부를 저장한다. 재접속 때 종류와 소유 라벨을 검사하고 중단된 준비는 초기화를 요구한다. | 소유권·준비 완료·재접속 계약을 재사용하는 후보. AWS endpoint·서비스 readiness·자원 이름은 새 상태 모델이 필요하다. |
| 초기화·정리 | 실습 루트에서 만든 소유 라벨로 컨테이너·네트워크만 찾는다. reset은 네트워크 정리 뒤 실습을 다시 만든다. | 소유 자원만 정리하는 원칙을 유지한다. 버킷·큐·데이터 볼륨을 어떤 단위로 보존/삭제할지는 미정이다. |
| 해설 시연 | 학생 실습을 복제한 별도 해설 경로와 준비 상태를 사용한다. 해설 종료 때 해설 네트워크를 정리한다. | 학생 버킷·큐와 해설 자원을 분리해야 한다. 공용 emulator의 이름 접두사만 쓸지 인스턴스까지 나눌지는 추가 판단이다. |
| 터미널·채점 보고 | 준비된 환경 변수를 실제 연습 터미널에 전달하고 `TestReport`에 판정·기대·실제를 반환한다. | endpoint·가짜 실습용 설정 전달과 학생 피드백에 활용할 수 있다. AWS 판정 로직은 별도다. |

근거: [영속 상태](https://github.com/jhs512/immersion-quest-3/blob/0d551472b3036ae6a0920e563d3ec5970f33ef8c/src/network_practice.rs#L36-L44), [준비·복구](https://github.com/jhs512/immersion-quest-3/blob/0d551472b3036ae6a0920e563d3ec5970f33ef8c/src/network_practice.rs#L327-L382), [정리·해설 종료](https://github.com/jhs512/immersion-quest-3/blob/0d551472b3036ae6a0920e563d3ec5970f33ef8c/src/network_practice.rs#L303-L325), [초기화](https://github.com/jhs512/immersion-quest-3/blob/0d551472b3036ae6a0920e563d3ec5970f33ef8c/src/git_practice.rs#L641-L650), [해설 복제](https://github.com/jhs512/immersion-quest-3/blob/0d551472b3036ae6a0920e563d3ec5970f33ef8c/src/git_practice.rs#L211-L224), [터미널 환경](https://github.com/jhs512/immersion-quest-3/blob/0d551472b3036ae6a0920e563d3ec5970f33ef8c/src/git_practice.rs#L447-L466), [상태 보고](https://github.com/jhs512/immersion-quest-3/blob/0d551472b3036ae6a0920e563d3ec5970f33ef8c/src/network_practice.rs#L785-L817).

현재 네트워크 구현은 이미지·CoreDNS·역할 이름·주소 배치·다음 홉·NET_ADMIN과 여덟 `kind` 분기에 결합되어 있다. Floci용 `s3`/`sqs`를 그 분기에 넣는 설계가 이미 지원되는 것은 아니다. 별도 AWS 실습 구성과 emulator adapter가 후보이며, 공통 수명주기 추출이 필요한지는 후속 설계 문제다. [고정 종류·이미지](https://github.com/jhs512/immersion-quest-3/blob/0d551472b3036ae6a0920e563d3ec5970f33ef8c/src/network_practice.rs#L7-L43), [주소·권한 구성](https://github.com/jhs512/immersion-quest-3/blob/0d551472b3036ae6a0920e563d3ec5970f33ef8c/src/network_practice.rs#L384-L474), [실제 분기별 채점](https://github.com/jhs512/immersion-quest-3/blob/0d551472b3036ae6a0920e563d3ec5970f33ef8c/src/network_practice.rs#L827-L1059).

## SDK·CLI·shell 방식의 적합성

일반 shell 채점은 명령의 순서와 성공 여부를 찾은 뒤 현재 폴더·파일 내용·폴더 목록까지 비교한다. Docker 터미널 채점도 명령 이력과 실제 이미지·컨테이너 상태를 함께 본다. 명령의 동등한 철자를 허용하는 정규화는 있지만, 결과가 같은 임의의 SDK 프로그램을 허용하는 채점기는 아니다. 반면 `check_shell`은 네트워크 구성일 때 바로 `check_network`로 넘겨 명령 이력 판정을 우회한다. AWS 실습도 목표가 서비스 상태라면 이처럼 문장·명령 문자열과 독립된 관찰 계약이 필요하다. [shell 검사](https://github.com/jhs512/immersion-quest-3/blob/0d551472b3036ae6a0920e563d3ec5970f33ef8c/src/shell_practice.rs#L277-L308), [Docker 검사](https://github.com/jhs512/immersion-quest-3/blob/0d551472b3036ae6a0920e563d3ec5970f33ef8c/src/docker_practice.rs#L329-L380).

일반 Docker Task에는 저작자가 준비한 `lab.sh`, 학생 파일, 실행 환경, Java 라이브러리 전달과 learn/check 분리의 선례가 있다. 그러나 현재 `valid_image`는 digest로 고정한 `busybox`·`postgres`·`mysql`·`nginx`만 허용한다. Floci 이미지를 넣은 콘텐츠는 현재 검사에서 거절된다. Java 라이브러리 묶음도 `h2`·`postgresql-jdbc`만 등록되어 있어 AWS SDK를 수업 선언만으로 받아오지 못한다. CLI 역시 설치·버전 고정·배포·실행 위치가 이 조사에서 마련된 것은 아니다. 따라서 “콘텐츠만 추가하면 된다”는 결론은 성립하지 않는다. [Docker Task 계약](https://github.com/jhs512/immersion-quest-3/blob/0d551472b3036ae6a0920e563d3ec5970f33ef8c/src/docker_lab.rs#L75-L106), [학생 실행](https://github.com/jhs512/immersion-quest-3/blob/0d551472b3036ae6a0920e563d3ec5970f33ef8c/src/docker_lab.rs#L800-L814), [learn/check 구분](https://github.com/jhs512/immersion-quest-3/blob/0d551472b3036ae6a0920e563d3ec5970f33ef8c/src/docker_lab.rs#L767-L771), [Java 준비](https://github.com/jhs512/immersion-quest-3/blob/0d551472b3036ae6a0920e563d3ec5970f33ef8c/src/docker_lab.rs#L840-L845), [등록 라이브러리](https://github.com/jhs512/immersion-quest-3/blob/0d551472b3036ae6a0920e563d3ec5970f33ef8c/src/library_sets.rs#L1-L25).

## S3·SQS 후보와 판정 원칙

이 절은 **후보 설계**다. Floci 특정 버전의 서비스·세부 API 호환성은 이 저장소 조사에서 검증하지 않았다. 구현 가능 확정이나 AWS 동작 전체의 재현 보장이 아니다.

| 후보 | 최소 관찰 흐름 | 학생 평가 후보 | 아직 확인할 것 |
| --- | --- | --- | --- |
| S3 객체 저장 | 준비된 입력 → 객체 저장 → 별도 읽기 → 같은 key 덮어쓰기 → 결과 비교 | 지정 자원에 기대 바이트·길이·metadata가 있고 다른 key/버킷은 보존되는지 API로 확인. 업로드 명령/출력 문구가 같아야 한다는 조건은 두지 않는다. | 사용 API·metadata·오류 코드 지원, SDK endpoint 설정, path-style 주소, 초기 자원과 정리 범위 |
| SQS 작업 인계 | 준비된 메시지 → 수신 → 처리 실패/재시도 관찰 → 처리 완료 후 삭제 | 고정 답안 문자열보다 메시지 본문·식별·가시성·완료 뒤 재등장 여부를 제한 시간 안에서 관찰하는 계약 | 수신은 상태를 바꾸므로 무해한 조회라고 간주할 수 없다. 전용 검사 lane/준비된 관찰자와 시간 제한, 근사 속성만으로 통과시켜도 되는지, 재시도·삭제 API 호환성 |

상태 목표라면 정답 SDK 코드·CLI의 여러 합법적 풀이가 같은 상태에서 통과해야 한다. 준비 코드는 실패하고, 정답은 통과하며, 잘못된 key·다른 큐·본문만 출력한 답·잘못된 endpoint 같은 오답이 거절되어야 한다. 채점기는 학생 상태를 정답 상태로 수리하지 않아야 한다. 특히 SQS는 관찰 자체가 상태를 바꿀 수 있으므로 S3 읽기와 동일한 검사 모델로 묶으면 안 된다. 이 원칙의 MQ 선례는 실제 프리픽스·경로 등을 확인하며 겉보기 통신 성공만으로는 통과시키지 않는 네트워크 오답 검사다. [검사 보고와 환경 오류 구분](https://github.com/jhs512/immersion-quest-3/blob/0d551472b3036ae6a0920e563d3ec5970f33ef8c/src/network_practice.rs#L785-L817), [겉보기 성공 오답 대조](https://github.com/jhs512/immersion-quest-3/blob/0d551472b3036ae6a0920e563d3ec5970f33ef8c/src/network_practice.rs#L1558-L1687), [MQ 정답·준비·오답 원칙](https://github.com/jhs512/immersion-quest-3/blob/0d551472b3036ae6a0920e563d3ec5970f33ef8c/AGENTS.md#L29-L39).

IP·라우팅·NAT 실습을 Floci로 대체하는 근거는 없다. 기존 수업은 실제 주소·프리픽스·경로·DNS·HTTP 식별 응답을 판정하고 NAT도 로컬 사설 주소 관찰이라고 명시한다. AWS API 상태를 다루려는 후보는 학습 대상이 다르다. 네트워크 보강을 선택하더라도 endpoint 경계의 응용 예제로 연결할 수 있을지 검토하는 수준이며, 실제 경로 학습의 대체 승인은 아니다. [학습·판정 범위](https://github.com/jhs512/immersion-quest-3/blob/0d551472b3036ae6a0920e563d3ec5970f33ef8c/docs/network-foundations-release.md#L9-L21), [실험의 한계](https://github.com/jhs512/immersion-quest-3/blob/0d551472b3036ae6a0920e563d3ec5970f33ef8c/docs/network-foundations-release.md#L31).

## Windows·macOS와 남은 검증

기존 실행기는 `MOLIP_DOCKER`, Windows 설치 경로, 사용자 범위 Docker Desktop, macOS Docker.app 및 Finder의 최소 PATH를 고려한다. 자식 PATH와 MSYS 경로 변환 설정도 있다. 네트워크 준비는 Docker Linux 컨테이너 모드를 요구한다. 일반 Compose는 등록 이미지·실습 내부 bind와 `127.0.0.1`의 Docker 할당 빈 포트만 허용한다. 따라서 고정 포트·호스트 localhost를 가정한 예제를 그대로 이식할 수 있다는 주장은 피해야 한다. [CLI 탐색·환경](https://github.com/jhs512/immersion-quest-3/blob/0d551472b3036ae6a0920e563d3ec5970f33ef8c/src/docker_lab.rs#L109-L160), [Linux 모드 확인](https://github.com/jhs512/immersion-quest-3/blob/0d551472b3036ae6a0920e563d3ec5970f33ef8c/src/network_practice.rs#L327-L338), [Compose 경계](https://github.com/jhs512/immersion-quest-3/blob/0d551472b3036ae6a0920e563d3ec5970f33ef8c/src/docker_lab.rs#L530-L570).

배포 문서는 Docker 실제 동작·네이티브 화면 검증을 Windows에서 수행하고 macOS 실제 실습은 별도 기기 검증 범위로 남겼다. 코드에 macOS 경로가 있다는 사실이 Floci의 Apple Silicon 이미지·마운트·호스트/컨테이너 통신을 검증했다는 뜻은 아니다. [검증 한계](https://github.com/jhs512/immersion-quest-3/blob/0d551472b3036ae6a0920e563d3ec5970f33ef8c/docs/network-foundations-release.md#L31).

후속 검증 후보는 (1) 사용자의 첫 적용 목적 확인, (2) Floci 버전·이미지 digest·S3/SQS API 계약의 공식 소스 확인, (3) 이미지/SDK/CLI 공급 경로와 endpoint 경계 설계, (4) 학생·해설·검사 상태 분리와 init/reset/cleanup 계약, (5) 준비 실패·정답·동등 풀이·대표 오답의 실제 판정, (6) Windows와 macOS Apple Silicon 양쪽에서 재접속·초기화·임의 포트·소유 자원 보존 확인이다. 이번 조사에서는 어느 단계도 구현·실행하지 않았다.

## 조사 수행과 확인 수준

저장소 소스와 정책을 직접 읽고 Context Mode로 필요한 출력만 처리했다. 조사 기준 커밋의 작업트리에서는 적용 영역의 ADR 및 별도 GLOSSARY 파일이 발견되지 않아 용어는 `CONTEXT.md`를 따랐다. Claude Code 직접 CLI에도 위 근거의 검토와 초안 작성을 맡겼다. 소스 열람·검토는 완료했지만 CLI의 파일 쓰기 권한이 거절되어 초안 파일은 생성되지 않았다. 그 검토 결과를 Codex가 실제 소스와 대조하고 이 단일 연구 파일로 작성했다. 런타임 실행·빌드·운영 게시 검증의 새 증거는 생성하지 않았다.

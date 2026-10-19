# 세 과정 개편 검증 기록

2026-10-19 기준. [전체 수업 구성](redesigned-courses.md)과 구분해 실행·게시·설치 검증의 범위와 한계를 기록한다.

## 제작과 게시

- 자바 백엔드 18수업·150스텝, AICE Associate 24수업·204스텝, 정보처리기사 실기 30수업·335스텝. 세 과정은 독립적이다.
- 수업별 PRD·대표 문제는 전체 재설계 위임 범위에서 승인 해시를 고정했다. 개별 수업을 사용자가 직접 검수했다고 표시하지 않는다.
- 공개 코스 저장소 세 개와 수업 저장소 72개를 게시했다. 실제 앱 로더가 불변 태그와 SHA-256을 확인해 689개의 고유 스텝을 읽었다. GitHub 진도 이슈의 생성·재조회·중복 방지·과거 완료 보존을 확인하고 검증용 이슈를 닫았다.
- Java의 현재 범위는 Git·Java·테스트·가벼운 React/Tailwind다. Spring Boot·DB는 후속 확장 범위이며 이미 구현한 수업으로 계산하지 않는다.

## 자동 검사와 실제 앱

| 범위 | 결과와 근거 |
| --- | --- |
| 최종 배포 코드의 전체 Rust 검사 | d9d5c2d의 깨끗한 소스에서 69묶음, 182 passed / 0 failed / 93 ignored, 619.93초. ignored인 실제 앱 검사는 별도로 실행했다. |
| 전체 새 수업 실행 | 2da0313 깨끗한 소스에서 추가58수업의 공개 입력·오답·해설 실행 통과. 최초14수업은 별도 통합 검사에 포함된다. 이후 구조 개선은 게시 콘텐츠의 바이트를 바꾸지 않았다. |
| 실제 GitHub 설치·진도 | 2da0313, 3코스/72수업/689스텝 및 진도 round-trip 통과, 65.35초. |
| Windows 핵심 화면과 실제 셸 | [39212491062](https://github.com/jhs512/immersion-quest-3/actions/runs/39212491062), d9d5c2d, workspace/terminal 모두 성공. 영문 Windows에서 깨지던 한글 출력은 자식 셸만 UTF-8로 초기화해 수정했다. |
| macOS ARM 구조 개선 | [39206901238](https://github.com/jhs512/immersion-quest-3/actions/runs/39206901238)의 ARM architecture job 성공. 같은 실행의 Windows 실패와 Intel 시간 초과를 전체 성공으로 바꾸어 표시하지 않는다. |
| macOS Intel 구조 개선 | 위 실행의 core23·수업 등록·업데이트·Git 상태·Python·CSV·Java·잘못된 순서·두 static수업·C다중포인터·TensorFlow가 통과했다. 전체 job은45분 제한으로 취소됐다. web/Git 검사는 별도 실행으로 대조한다. |
| 실제 React/Tailwind와 브라우저 | [39210447089](https://github.com/jhs512/immersion-quest-3/actions/runs/39210447089), Windows·Mac ARM·Intel 모두 성공. 학생의 살아 있는 iframe 보존과 새 npm/Node 경로를 검사했다. |
| Python 배포 환경과 신경망 | [39203351259](https://github.com/jhs512/immersion-quest-3/actions/runs/39203351259), 세 플랫폼의 release-runtime/neural 여섯 job 성공. Keras2 기준 환경과 실제 배포 패키지 환경을 구분했다. |
| 정처기 이론·Git | [39203806335](https://github.com/jhs512/immersion-quest-3/actions/runs/39203806335), 세 플랫폼 git/theory 여섯 job 성공. 구조 개선 후 [39212733296](https://github.com/jhs512/immersion-quest-3/actions/runs/39212733296)의 세 플랫폼 실제 Git/해설/초기화 검사도 모두 성공했다. |
| 설치 파일 사전 검사 | [39207094610](https://github.com/jhs512/immersion-quest-3/actions/runs/39207094610), Windows 설치·제거와 Mac ARM/Intel 서명·DMG·아키텍처·실행 통과. main 외 실행이므로 이 결과는 정식 릴리즈 게시를 뜻하지 않는다. |

검사에서 초기 설치를 이미 통과한 pinned compiler/JUnit 캐시를 재사용한 실행과 빈 환경 설치 검사를 구분했다. 캐시를 재사용했다고 새 학습자 자료나 답안을 공유한 것은 아니다.

## 구조 개선

수업 등록은 catalog 한곳에서 Python 제작기·Rust 등록·검증 화면으로 전달한다. 해설은 학습자 작업 공간과 세션 소유권을 모아 늦은 비동기 종료가 다음 답안을 덮어쓰지 않게 했다. 실제 동일 DOM 소유자 변경은 실패를 먼저 확인하고 수정했다. 잘못된 순서 입력의 freeze는 수정 전에도 통과했으므로 재현했다고 주장하지 않는다.

## 남은 수동 확인 범위

- 실제 음성 청취는 다운로드·캐시·재생 동기화 자동 검사와 다르다. 모든 해설을 사람이 들었다고 보고하지 않는다.
- 실제 Windows F11과 Unicode 입력·복사는 확인했으나, 물리 IME 자모 조합 및 Mac의 실제 OS 키보드·clipboard 전체 검증 증거는 없다. Computer Use 재시도는 창 좌표13×13 오류로 중단했다. DOM 키 이벤트를 물리 입력 통과로 계산하지 않는다.
- Windows 코드 서명과 Apple notarization은 구성되어 있지 않다. Mac의 ad-hoc codesign 검사 통과를 Developer ID 서명으로 표현하지 않는다.

원본 결과는 로컬 target/player-pilot-audit/, 진행 이력과 티켓은 .scratch/player-content-redesign/에 보관한다. 실패·취소된 실행도 삭제하지 않는다.

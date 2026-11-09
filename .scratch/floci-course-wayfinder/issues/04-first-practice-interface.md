# 첫 실습은 AWS CLI로 원리를 확인할 것인가 SDK 코드로 시작할 것인가

Labels: wayfinder:grilling
Type: grilling
Status: resolved
Blocked by: 01, 02, 03
Parent: [Floci를 활용한 MQ 클라우드 실습의 적용 경로](../map.md)

## Question

첫 학습 목표가 정해지면, 학생은 준비된 AWS CLI 명령의 작은 변경으로 서비스 동작을 관찰할 것인가, SDK가 준비된 Java 등 코드의 작은 변경으로 시작할 것인가? 도구 설정량보다 교육 목표와 선수 지식, MQ의 라이브러리·실행 환경 제약을 기준으로 선택한다.

## Comments

기존 Java 라이브러리 지원을 AWS SDK 지원으로 간주하지 않는다. MQ 실행 환경과 공식 서비스 지원 조사의 근거가 정리되고 첫 학습 목표가 선택된 뒤 사용자와 결정한다.

## Answer

2026-11-09 사용자는 준비된 AWS CLI 명령의 CIDR 한 곳을 고치는 대표 문제와 첫 수업 PRD를 제시받고 “고고”로 진행을 승인했다. 첫 수업은 CLI로 자원 관계·배치를 관찰한다. 자바 서버는 준비 이미지이며 패키징이나 AWS SDK 도입은 첫 수업 목표로 추가하지 않는다. 이후 서비스 수업의 SDK 선택까지 승인된 것은 아니다.

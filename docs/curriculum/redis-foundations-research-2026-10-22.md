# Redis 기초·실전 확장 조사

조사일: 2026-10-22. 목적은 Java 백엔드 코스 확장 **계획의 근거** 제공이다. 수업 본문·문제·정답·설치 절차가 아니다. 아래의 학습 순서와 실습 소재는 조사자의 교육 설계 제안이며, Redis의 동작 사실과 구분한다.

## 진입점과 단계 제안

Redis는 캐시 전용 도구보다 넓은 자료구조 서버로 소개하는 편이 적절하다. 키에 자료형이 있는 값을 보관하고, 그 자료형에 맞는 명령을 서버에 요청한다는 모형부터 시작한다. **제안 순서**는 CLI의 명령·반환값 관찰 → Spring 없는 작은 Java 클라이언트 → 자료형으로 기능 만들기 → 동시성·장애 관찰 → HTTP·Spring·DB와 통합이다. 따라서 SQL이나 Spring Cache를 Redis 첫 수업의 선수조건으로 만들 필요가 없다. 공식 기초 안내 역시 자료구조와 명령을 중심으로 구성되어 있다. [Redis data types](https://redis.io/docs/latest/develop/data-types/), [Redis data store quick start](https://redis.io/docs/latest/develop/get-started/data-store/)

1. **키·값·수명**: 서버와 클라이언트, `PING`, `SET`/`GET`, 없는 키, `DEL`, `EXISTS`, `TYPE`, `INCR`, 키 이름 충돌 방지부터 다룬다. 콜론은 실제 네임스페이스 기능이 아닌 이름 규약이다. 키 탐색은 작은 예제의 `KEYS`와 점진적 `SCAN`의 차이를 보여 주고, 정규 애플리케이션 흐름에 `KEYS *`를 넣지 않는다. [Keys and values](https://redis.io/docs/latest/develop/using-commands/keyspace/), [INCR](https://redis.io/docs/latest/commands/incr/)
2. **TTL**: `EXPIRE`, `TTL`, `SET ... EX/PX`, `PERSIST`를 키 수명 관찰에 사용한다. 값을 덮어쓰는 `SET`이 기존 TTL을 지울 수 있다는 점과 수정 명령 전체가 같은 방식으로 TTL을 다루지는 않는다는 점을 구분한다. 일회용 코드·임시 초안 같은 소재로 시작한 뒤 세션에 연결한다. [EXPIRE](https://redis.io/docs/latest/commands/expire/), [SET](https://redis.io/docs/latest/commands/set/)
3. **자료구조 선택**: 같은 요구사항을 문자열 직렬화와 전용 자료형으로 각각 표현하고, 원하는 조회·변경 연산에 맞춰 고른다. 그다음 Java에서 명령 결과·null·오류·직렬화·연결 수명을 관찰하도록 확장한다. 공식 문서에는 Jedis와 Lettuce 예제가 함께 있다. [Compare data types](https://redis.io/docs/latest/develop/data-types/compare-data-types/), [Java cache-aside example](https://redis.io/docs/latest/develop/use-cases/cache-aside/java-jedis/)

## 자료형별 실전 소재

아래 명령은 각 단원의 범위 후보이며 전 명령 암기를 요구하는 목록이 아니다. 자료형별로 삽입·조회·변경·삭제와 경계조건을 확인하는 작은 기능을 우선한다. [Compare data types](https://redis.io/docs/latest/develop/data-types/compare-data-types/)

| 자료형 | 범위 후보와 기능 소재 | 반드시 구분할 성질 | 공식 근거 |
| --- | --- | --- | --- |
| String | `SET`, `GET`, `INCR`; 조회수·임시 값 | 숫자 증가도 String 연산이며 `GET` 후 `SET`과 `INCR`은 동시성 면에서 다름 | [INCR](https://redis.io/docs/latest/commands/incr/) |
| Hash | `HSET`, `HGET`, `HMGET`, `HGETALL`, `HINCRBY`; 프로필·장바구니 | 키 안의 필드와 전체 키를 구별; 중첩 JSON과 같지 않음 | [Hashes](https://redis.io/docs/latest/develop/data-types/hashes/) |
| List | `LPUSH`/`RPUSH`, `LPOP`/`RPOP`, `LRANGE`, `LTRIM`; 최근 기록·단순 작업 대기열 | 순서·중복을 보존; pop은 제거이므로 처리 완료 ACK를 제공하는 대기열로 단정하지 않음 | [Data types](https://redis.io/docs/latest/develop/data-types/), [LPOP](https://redis.io/docs/latest/commands/lpop/) |
| Set | `SADD`, `SISMEMBER`, `SCARD`, `SINTER`/`SUNION`/`SDIFF`; 좋아요·공통 관심사 | 중복 없는 집합이며 출력 순서를 보장하지 않음 | [Sets](https://redis.io/docs/latest/develop/data-types/sets/) |
| Sorted Set | `ZADD`, `ZINCRBY`, `ZRANGE`, `ZRANK`; 순위표·점수 구간 조회 | member는 유일하며 score에 따라 정렬; 단순 List와 비교 | [Sorted sets](https://redis.io/docs/latest/develop/data-types/sorted-sets/) |
| Bitmap | `SETBIT`, `GETBIT`, `BITCOUNT`, `BITOP`; 출석·일별 활동 플래그 | String의 비트 연산; ID와 bit offset 매핑을 설계해야 함 | [Bitmaps](https://redis.io/docs/latest/develop/data-types/strings/bitmaps/) |
| HyperLogLog | `PFADD`, `PFCOUNT`, `PFMERGE`; 일별·주간 순방문자 | 정확한 명단·membership 조회 대신 고유 개수의 근사 추정 | [HyperLogLog](https://redis.io/docs/latest/develop/data-types/probabilistic/hyperloglogs/) |
| GEO | `GEOADD`, `GEODIST`, `GEOSEARCH`; 주변 장소 검색 | 좌표·거리 단위와 반경/상자 조건; 범용 GIS 전체를 제공하는 것으로 소개하지 않음 | [Geospatial](https://redis.io/docs/latest/develop/data-types/geospatial/) |

## 명령 묶음과 동시성

- **Pipeline**은 매 명령의 응답을 기다리지 않고 여러 요청을 보내 RTT와 I/O 비용을 줄이는 성능 기법이다. 그 자체를 여러 명령의 격리·원자성 보장으로 가르치면 안 된다. 앞 명령 결과를 읽어 다음 쓰기를 결정하는 작업에는 별도의 실행 모형이 필요하다. [Pipelining](https://redis.io/docs/latest/develop/using-commands/pipelining/)
- **`MULTI`/`EXEC`**는 명령을 모아 다른 클라이언트 명령이 중간에 끼지 않게 실행한다. `WATCH`는 감시한 키가 바뀌면 실행 전에 전체 묶음을 취소하는 낙관적 CAS이며, 충돌 후 재시도는 클라이언트 설계다. `DISCARD`, 큐에 넣을 때 발견한 오류, 실행 중 타입 오류를 구분해야 한다. 실행 중 실패한 명령 때문에 앞선 성공을 롤백하지 않으며 나머지 명령도 실행한다. [Transactions](https://redis.io/docs/latest/develop/using-commands/transactions/)
- **Lua**는 읽기·분기·쓰기를 서버에서 원자적으로 실행하지만 실행 중 서버를 막으므로 짧고 제한된 작업으로 다룬다. 원자적 실행을 SQL식 오류 롤백과 같은 뜻으로 쓰지 않는다. 입력·타입·전제조건은 쓰기 전에 검증하는 방향으로 설계한다. 쓰기 후 실행을 안전하게 취소하는 기능으로 `SCRIPT KILL`을 소개해서도 안 된다. [Scripting with Lua](https://redis.io/docs/latest/develop/programmability/eval-intro/), [Redis의 롤백 설명](https://redis.io/blog/you-dont-need-transaction-rollbacks-in-redis/), [SCRIPT KILL](https://redis.io/docs/latest/commands/script-kill/)

## 기능 통합 순서와 실패 관찰

- **캐시**: 느린 원본 조회 함수를 먼저 두고 hit/miss, TTL, 쓰기 후 `DEL` 무효화, 오래된 값, 동시 만료를 관찰한다. 이 단계의 원본은 DB 대신 메모리 저장소여도 된다는 것은 교육 설계 제안이다. 이후 DB를 붙여 cache-aside로 발전시킨다. TTL·무효화만으로 DB와 Redis가 하나의 강한 일관성 트랜잭션이 된다고 설명하지 않는다. [Cache-aside](https://redis.io/docs/latest/develop/use-cases/cache-aside/)
- **세션**: 서버 인스턴스 간 공유 상태, 세션 ID→Hash/String, 유휴 만료와 갱신, 로그아웃 삭제를 TTL 뒤에 배치한다. Redis가 사라지면 복원 가능한 캐시와 사용자 상태의 손실 의미가 다르므로 세션 저장에는 영속성·메모리 정책을 연결한다. [Session store](https://redis.io/docs/latest/develop/use-cases/session-store/)
- **요청 제한**: `INCR`+TTL로 고정 구간 카운터를 먼저 만든다. 증가와 최초 만료 설정 사이에서 클라이언트가 멈추면 키가 남는 경합을 보여 주고 `MULTI` 또는 조건부 로직이 있는 Lua로 개선한다. 구간 경계의 몰림을 논의한 뒤 Sorted Set 기반 이동 구간 등으로 확장하는 것을 제안한다. [INCR의 rate limiter patterns](https://redis.io/docs/latest/commands/incr/)
- **Pub/Sub**: `SUBSCRIBE`/`PUBLISH`로 살아 있는 구독자에게 알리는 경험을 먼저 제공한다. 전달은 at-most-once이며 구독자 단절·처리 실패로 놓친 메시지를 재생하지 못한다. 채팅 알림·화면 갱신 신호와 보존해야 하는 업무 이벤트를 구분한다. [Pub/Sub delivery semantics](https://redis.io/docs/latest/manual/pubsub/), [Java Pub/Sub example](https://redis.io/docs/latest/develop/use-cases/pub-sub/java-jedis/)
- **Streams**: `XADD`/`XRANGE`/`XREAD`의 보관·다시 읽기에서 시작해 `XGROUP`, `XREADGROUP`, `XACK`, `XPENDING`, `XCLAIM`/`XAUTOCLAIM`으로 확장한다. ACK는 처리 완료 기록이며 삭제와 같지 않다. reclaim은 유휴 pending 작업의 소유권을 넘기는 과정이므로 재처리가 생길 수 있다. 외부 부수효과 직후 ACK 전에 죽는 사례로 멱등성·중복 방지의 필요를 다룬다. 보존·trim·영속성 설정에 따른 유실 가능성을 별도로 검토한다. [Streams](https://redis.io/docs/latest/develop/data-types/streams/), [Streaming use case](https://redis.io/docs/latest/develop/use-cases/streaming/)

## 운영 기초와 고급 주제의 경계

- **영속성**: RDB는 특정 시점 스냅샷, AOF는 쓰기 연산 기록과 재생이다. 재시작 실험은 영속성 없음/RDB/AOF를 비교하고, 저장 주기·fsync 정책과 성능·유실 허용 범위를 연결한다. 메모리에서 빠르게 응답한다는 사실과 디스크에 안전하게 남았다는 사실은 별개다. [Persistence](https://redis.io/docs/latest/management/persistence/)
- **TTL과 퇴거**: TTL은 시간에 따른 만료이고 eviction은 `maxmemory` 압박에 따른 정책이다. LRU/LFU, allkeys/volatile, `noeviction`의 쓰기 오류를 구분한다. TTL이 아직 남은 키도 퇴거될 수 있으므로 세션·작업 이벤트·캐시를 같은 손실 정책으로 다룰지 판단하게 한다. [Key eviction](https://redis.io/docs/latest/reference/eviction/), [EXPIRE](https://redis.io/docs/latest/commands/expire/)
- **복제·장애 전환**: 기본 복제는 비동기이며 Sentinel은 비클러스터 Redis의 감시·장애 전환을 맡는다. 복제본·Sentinel을 추가해도 승인된 쓰기의 유실 가능성이 사라지지 않는다. `WAIT` 역시 강한 일관성을 자동 제공하지 않는다. 따라서 Streams ACK나 재시도와 조합했다는 이유만으로 end-to-end exactly-once를 보장한다고 쓰지 않는다. [Replication](https://redis.io/docs/latest/operate/oss_and_stack/management/replication/), [Sentinel](https://redis.io/docs/latest/operate/oss_and_stack/management/sentinel/)
- **분산 락은 후반 선택**: 단일 명령 원자성, 여러 클라이언트 경합, TTL 만료, 고유 소유권, 안전한 해제, 프로세스 정지·네트워크 단절·복제 지연을 다룬 뒤 배치하는 것을 제안한다. `SET NX EX`만 보여 주고 모든 임계구역 문제가 해결된다고 설명하지 않는다. 기초 요청 제한과 자료구조 기능의 필수 선수조건으로 두지 않는다. [SET의 locking pattern](https://redis.io/docs/latest/commands/set/), [Replication](https://redis.io/docs/latest/operate/oss_and_stack/management/replication/)

## 버전 고정과 선택 확장

제작 전에 Redis 서버 배포판·정확한 버전, Java 클라이언트 버전, 사용 가능 명령을 기록하고 그 조합으로 범위를 확정해야 한다. 공식 `latest` 문서의 예제에 새 명령·옵션이 계속 추가되므로 검색 결과를 그대로 공통 기초로 옮기지 않는다. 예를 들어 `XAUTOCLAIM`은 6.2+, Hash field TTL은 7.4+, `HSETEX`는 8.0+이며 Streams의 그룹별 삭제 제어는 8.2+ 기능이다. [Streams command versions](https://redis.io/docs/latest/develop/data-types/streams/), [Hashes command versions](https://redis.io/docs/latest/develop/data-types/hashes/)

JSON·Search, Bloom 계열, 시계열·벡터 기능은 서버 기능 확인을 거친 선택 확장으로 둔다. Redis 8은 JSON·Search·여러 확률형 자료구조 등을 통합하지만, 이를 과거 모든 OSS 버전의 기본 기능으로 쓰면 틀린다. 확장에서도 먼저 기존 String/Hash/Set으로 해결할 요구와 새 기능이 필요한 요구를 비교한다. [Redis 8 release notes](https://redis.io/docs/latest/operate/rc/changelog/version-release-notes/8-0/)

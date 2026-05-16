# counter (접속 통계)

## 개요

- **카테고리**: statistics
- **역할**: 사이트 방문자 카운트. 일/월 단위 집계.

## 주요 클래스

| 클래스 | 파일 |
|---|---|
| `Counter` | `counter.class.php` |
| `CounterController` | `counter.controller.php` |
| `CounterModel` | `counter.model.php` |
| `CounterAdminView` | `counter.admin.view.php` |

## 주요 액션 (3개)

| 액션 | 비고 |
|---|---|
| `dispCounterAdminIndex` | 통계 대시보드 (admin_index) |
| `getWeeklyPageView` | 주간 페이지뷰 조회 (root) |
| `getWeeklyUniqueVisitor` | 주간 순방문자 조회 (root) |

일일 집계는 모듈 액션이 아니라 `counter` **애드온** + 모델 메서드로 수집·계산된다 (별도 cron 액션 없음).

## DB 스키마

| 테이블 | 정의 파일 |
|---|---|
| `counter_log` | `schemas/counter_log.xml` — 방문 로그 |
| `counter_status` | 일/월 통계 |
| `counter_site_status` | 사이트(도메인) 단위 통계 |

(`counter`라는 단일 테이블은 없다 — 모든 데이터는 위 3개 테이블에 분산.)

## 동작

- 동명 애드온([../29-addons/counter.md](../29-addons/counter.md))이 모든 페이지 진입을 기록.
- 모듈은 집계/표시.

## 관련 위젯

- `counter_status` 위젯이 사이트에 통계 표시 ([../30-widgets/counter_status.md](../30-widgets/counter_status.md)).

## 관련

- 애드온: [../29-addons/counter.md](../29-addons/counter.md)
- 위젯: [../30-widgets/counter_status.md](../30-widgets/counter_status.md)

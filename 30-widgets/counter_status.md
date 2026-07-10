# counter_status (위젯)

## 개요

- **목적**: 사이트 접속 통계를 표시. 오늘/어제/총 방문자.

## proc() 인자 (`$args`)

`widgets/counter_status/conf/info.xml`에 **사용자 정의 extra_vars가 없다**. 기본 스킨/컬러셋 외에 별도 인자가 노출되지 않는다.

| 인자 | 의미 |
|---|---|
| `$args->skin` | 호출자가 선택하는 스킨. `proc()`에는 fallback이 없음 |
| `$args->colorset` | 컬러셋. 누락 시 공통 실행기가 빈 문자열로 초기화 |

표시 항목(오늘/어제/총합/차트 등)은 모두 **스킨이 결정**한다.

## 컨텍스트로 전달되는 변수

`counter_status.class.php`의 `proc()`이 `CounterModel::getStatus()`를 호출하고 다음 키를 `Context::set`으로 주입한다:

| 키 | 의미 |
|---|---|
| `total_counter` | 누적 (key `'00000000'`로 조회된 값) |
| `today_counter` | 오늘 (`date('Ymd')`) |
| `yesterday_counter` | 어제 (`REQUEST_TIME - 86400`) |
| `colorset` | 선택된 컬러셋 |

스킨 템플릿이 이 변수들을 직접 출력한다.

## 데이터 출처

`counter` 모듈의 `counter_status` 테이블 ← `counter` 애드온이 `CounterController::counterExecute()`로 실시간 누적/집계 (별도 cron 액션 없음).

## 스킨

`widgets/counter_status/skins/default/counter_status.html` (진입 템플릿명 = 위젯명).

## 관련

- counter 모듈: [../28-modules/counter.md](../28-modules/counter.md)
- counter 애드온: [../29-addons/counter.md](../29-addons/counter.md)

# counter (애드온)

## 개요

- **목적**: 설치 완료된 HTML 요청 중 `admin` 모듈과 crawler를 제외한 방문을 카운트해 통계 모듈에 데이터 공급.

## hook 위치

`before_display_content` — 본문 생성 후, admin 모듈/봇/JSON 등 응답은 제외하고 1회 카운트.

## 동작

`addons/counter/counter.addon.php` (실제 코드):

```php
if ($called_position == 'before_display_content'
    && Context::get('module') != 'admin'
    && Context::getResponseMethod() == 'HTML'
    && Context::isInstalled()
    && !isCrawler())
{
    $oCounterController = getController('counter');
    $oCounterController->counterExecute();
}
```

`CounterController::counterExecute()`가 `counter_status`/`counter_log` 테이블에 누적 집계한다 (`CounterModel::isLogged()`로 오늘·접속 IP의 첫 방문 여부를 판별해, 첫 방문이면 `counter_status`의 오늘 날짜(`regdate=Ymd`) 일별 행과 누적 총계 행(`regdate=0`)의 `unique_visitor`·`pageview`를 `+1` 갱신하고 `counter_log`에 접근 로그 1행을 남기며, 재방문이면 `pageview`만 `+1`한다. 월별/주별/연별 통계는 별도 롤업 없이 조회 시 `CounterModel::getHourlyStatus()`가 일별 `counter_status` 행을 `SUM`으로 합산해 산출한다).

## 위젯

`counter_status` 위젯이 결과를 표시.

## 관련

- 동명 모듈: [../28-modules/counter.md](../28-modules/counter.md)
- 위젯: [../30-widgets/counter_status.md](../30-widgets/counter_status.md)

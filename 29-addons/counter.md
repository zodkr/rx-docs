# counter (애드온)

## 개요

- **목적**: 모든 페이지 진입을 카운트해 통계 모듈에 데이터 공급.

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

`CounterController::counterExecute()`가 `counter`/`counter_log`/`counter_status` 테이블에 누적 집계한다 (실시간 + 단계적 일별/월별 집계).

## 위젯

`counter_status` 위젯이 결과를 표시.

## 관련

- 동명 모듈: [../28-modules/counter.md](../28-modules/counter.md)
- 위젯: [../30-widgets/counter_status.md](../30-widgets/counter_status.md)

<!-- rx-docs tools 브랜치의 deprecated/generate.py 가 생성. 직접 수정 금지. 대체 API는 같은 브랜치의 deprecated/overrides.json 에서 고친다. -->
# JavaScript(common/js)에서 deprecated 처리된 함수

검증 기준: Rhymix 2.1.36, 커밋 `1ae6ce181`, 2026-09-02. 규칙과 열 설명은 [README.md](README.md). 항목 수: 29.

| 심볼 | 위치 | 시점 | 유래 | 대체 API | 비고 |
|---|---|---|---|---|---|
| `getCookie()` | `common/js/common.js:1630` | 2.1 | XE | `Rhymix.cookie.get(name)` |  |
| `setCookie()` | `common/js/common.js:1643` | 2.1 | XE | `Rhymix.cookie.set(name, value, options)` |  |
| `doChangeLangType()` | `common/js/common.js:1664` | 2.1 | XE | 확인 필요 |  |
| `doCallModuleAction()` | `common/js/common.js:1693` | 2.1 | XE | `Rhymix.ajax(action, params, callback)` |  |
| `rhymix_alert_close()` | `common/js/common.js:1723` | 2.1 | 2.0 | 확인 필요 |  |
| `rhymix_alert()` | `common/js/common.js:1738` | 2.1 | 2.0 | 확인 필요 |  |
| `move_url()` | `common/js/common.js:1762` | 2.1 | XE | 확인 필요 |  |
| `setFixedPopupSize()` | `common/js/common.js:1785` | 2.1 | XE | 확인 필요 |  |
| `displayMultimedia()` | `common/js/common.js:1821` | 2.1 | XE | 확인 필요 |  |
| `sendMailTo()` | `common/js/common.js:1890` | 2.1 | XE | 확인 필요 |  |
| `viewSkinInfo()` | `common/js/common.js:1901` | 2.1 | XE | 확인 필요 |  |
| `xSleep()` | `common/js/common.js:1914` | 2.1 | XE | 확인 필요 |  |
| `isDef()` | `common/js/common.js:1930` | 2.1 | XE | 확인 필요 |  |
| `is_def()` | `common/js/common.js:1948` | 2.1 | XE | 확인 필요 |  |
| `ucfirst()` | `common/js/common.js:1959` | 2.1 | XE | 확인 필요 |  |
| `get_by_id()` | `common/js/common.js:1970` | 2.1 | XE | 확인 필요 |  |
| `GetObjLeft()` | `common/js/common.js:1981` | 2.1 | XE | 확인 필요 |  |
| `GetObjTop()` | `common/js/common.js:1992` | 2.1 | XE | 확인 필요 |  |
| `getOuterHTML()` | `common/js/common.js:2003` | 2.1 | XE | 확인 필요 |  |
| `replaceOuterHTML()` | `common/js/common.js:2014` | 2.1 | XE | 확인 필요 |  |
| `toggleDisplay()` | `common/js/common.js:2026` | 2.1 | XE | 확인 필요 |  |
| `toggleSecuritySignIn()` | `common/js/common.js:2037` | 2.1 | XE | 확인 필요 |  |
| `completeMessage()` | `common/js/common.js:2052` | 2.1 | XE | 확인 필요 |  |
| `reloadDocument()` | `common/js/common.js:2064` | 2.1 | XE | 확인 필요 |  |
| `open_calendar()` | `common/js/common.js:2074` | 2.1 | XE | 확인 필요 |  |
| `displayPopupMenu()` | `common/js/common.js:2087` | 2.1 | XE | 확인 필요 |  |
| `createPopupMenu()` | `common/js/common.js:2100` | 2.1 | XE | 확인 필요 |  |
| `chkPopupMenu()` | `common/js/common.js:2110` | 2.1 | XE | 확인 필요 |  |
| `procFilter()` | `common/js/xml_js_filter.js:395` | XE | XE | 확인 필요 |  |

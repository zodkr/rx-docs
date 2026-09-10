<!-- rx-docs tools 브랜치의 deprecated/generate.py 가 생성. 직접 수정 금지. 대체 API는 같은 브랜치의 deprecated/overrides.json 에서 고친다. -->
# JavaScript(common/js)에서 deprecated 처리된 함수

검증 기준: Rhymix 2.1.36, 커밋 `1ae6ce181`, 2026-09-02. 규칙과 열 설명은 [README.md](README.md). 항목 수: 29.

| 심볼 | 위치 | 시점 | 유래 | 대체 API | 비고 |
|---|---|---|---|---|---|
| `getCookie()` | `common/js/common.js:1630` | 2.1 | XE | `Rhymix.cookie.get(name)` |  |
| `setCookie()` | `common/js/common.js:1643` | 2.1 | XE | `Rhymix.cookie.set(name, value, options)` |  |
| `doChangeLangType()` | `common/js/common.js:1664` | 2.1 | XE | `setLangType(lang) 후 location.reload()` |  |
| `doCallModuleAction()` | `common/js/common.js:1693` | 2.1 | XE | `Rhymix.ajax(action, params, callback)` |  |
| `rhymix_alert_close()` | `common/js/common.js:1723` | 2.1 | 2.0 | 없음 | 코어 내부용. 메시지는 서버 setMessage()가 자동 표시 |
| `rhymix_alert()` | `common/js/common.js:1738` | 2.1 | 2.0 | 없음 | 코어 내부용. 메시지는 서버 setMessage()가 자동 표시 |
| `move_url()` | `common/js/common.js:1762` | 2.1 | XE | `redirect(url) 또는 winopen(url)` |  |
| `setFixedPopupSize()` | `common/js/common.js:1785` | 2.1 | XE | 없음 | 팝업 크기 자동 조정 제거 |
| `displayMultimedia()` | `common/js/common.js:1821` | 2.1 | XE | 없음 | document.writeln 기반. 멀티미디어 삽입은 에디터 컴포넌트 |
| `sendMailTo()` | `common/js/common.js:1890` | 2.1 | XE | `location.href = 'mailto:' + address` |  |
| `viewSkinInfo()` | `common/js/common.js:1901` | 2.1 | XE | `popopen(url, 'SkinInfo')` | url은 dispModuleSkinInfo 액션 |
| `xSleep()` | `common/js/common.js:1914` | 2.1 | XE | 없음 | busy-wait. setTimeout() 사용 |
| `isDef()` | `common/js/common.js:1930` | 2.1 | XE | `typeof x !== 'undefined'` |  |
| `is_def()` | `common/js/common.js:1948` | 2.1 | XE | `x != null` |  |
| `ucfirst()` | `common/js/common.js:1959` | 2.1 | XE | `str.charAt(0).toUpperCase() + str.slice(1)` |  |
| `get_by_id()` | `common/js/common.js:1970` | 2.1 | XE | `document.getElementById(id)` |  |
| `GetObjLeft()` | `common/js/common.js:1981` | 2.1 | XE | `$(obj).offset().left` |  |
| `GetObjTop()` | `common/js/common.js:1992` | 2.1 | XE | `$(obj).offset().top` |  |
| `getOuterHTML()` | `common/js/common.js:2003` | 2.1 | XE | `obj.outerHTML` | 원본은 $(obj).html().trim()(innerHTML) |
| `replaceOuterHTML()` | `common/js/common.js:2014` | 2.1 | XE | `$(obj).replaceWith(html)` |  |
| `toggleDisplay()` | `common/js/common.js:2026` | 2.1 | XE | `$('#' + id).toggle()` |  |
| `toggleSecuritySignIn()` | `common/js/common.js:2037` | 2.1 | XE | 없음 | HTTP/HTTPS 전환 개념 제거 |
| `completeMessage()` | `common/js/common.js:2052` | 2.1 | XE | `alert(ret_obj.message); location.reload()` |  |
| `reloadDocument()` | `common/js/common.js:2064` | 2.1 | XE | `location.reload()` |  |
| `open_calendar()` | `common/js/common.js:2074` | 2.1 | XE | 없음 | no-op. 날짜 입력은 <input type="date"> |
| `displayPopupMenu()` | `common/js/common.js:2087` | 2.1 | XE | `Rhymix.displayPopupMenu(ret_obj, response_tags, params)` |  |
| `createPopupMenu()` | `common/js/common.js:2100` | 2.1 | XE | 없음 | no-op |
| `chkPopupMenu()` | `common/js/common.js:2110` | 2.1 | XE | 없음 | no-op |
| `procFilter()` | `common/js/xml_js_filter.js:395` | XE | XE | 없음 | filter_func(form)을 직접 호출. 폼 제출은 Rhymix.ajax() |

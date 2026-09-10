<!-- rx-docs tools 브랜치의 deprecated/generate.py 가 생성. 직접 수정 금지. 대체 API는 같은 브랜치의 deprecated/overrides.json 에서 고친다. -->
# Rhymix 2.0.x에서 deprecated 처리된 API

검증 기준: Rhymix 2.1.36, 커밋 `1ae6ce181`, 2026-09-02. 규칙과 열 설명은 [README.md](README.md). 항목 수: 60.

## classes/

| 심볼 | 위치 | 유래 | 대체 API | 비고 |
|---|---|---|---|---|
| `Context::addSSLAction()` | `classes/context/Context.class.php:2115` | XE | 없음 | 액션별 SSL 개념 제거, no-op. 사이트 전체 HTTPS는 config('url.ssl'); 2.0.0에서 표시 |
| `Context::addSSLActions()` | `classes/context/Context.class.php:2127` | XE | 없음 | 액션별 SSL 개념 제거, no-op. 사이트 전체 HTTPS는 config('url.ssl'); 2.0.0에서 표시 |
| `Context::subtractSSLAction()` | `classes/context/Context.class.php:2139` | XE | 없음 | 액션별 SSL 개념 제거, no-op. 사이트 전체 HTTPS는 config('url.ssl'); 2.0.0에서 표시 |
| `Context::getSSLActions()` | `classes/context/Context.class.php:2151` | XE | 없음 | 액션별 SSL 개념 제거, no-op. 사이트 전체 HTTPS는 config('url.ssl'); 2.0.0에서 표시 |
| `Context::isExistsSSLAction()` | `classes/context/Context.class.php:2162` | XE | 없음 | 액션별 SSL 개념 제거, no-op. 사이트 전체 HTTPS는 config('url.ssl'); 2.0.0에서 표시 |
| `Context::getBodyClass()` | `classes/context/Context.class.php:2622` | XE | `Context::getBodyClassList()` | 원본은 class 속성 문자열, 대체는 배열; 2.0.24에서 표시 |
| `FileHandler::clearStatCache()` | `classes/file/FileHandler.class.php:934` | 2.0 | `clearstatcache(true, $path)` | PHP 내장; 2.0.0에서 표시; 코어 호출 있음 |
| `FileHandler::invalidateOpcache()` | `classes/file/FileHandler.class.php:957` | 2.0 | `opcache_invalidate($path, true)` | PHP 내장. Rhymix\Framework\Storage의 쓰기 메서드는 내부에서 자동 처리; 2.0.0에서 표시; 코어 호출 있음 |

## common/framework/

| 심볼 | 위치 | 유래 | 대체 API | 비고 |
|---|---|---|---|---|
| `Rhymix\Framework\DB::create()` | `common/framework/DB.php:1445` | 2.0 | `DB::getInstance()` | 2.0.0에서 표시; 코어 호출 있음 |
| `Rhymix\Framework\DB::db_fetch_object()` | `common/framework/DB.php:1456` | 2.0 | `$stmt->fetchObject()` | 2.0.0에서 표시 |
| `Rhymix\Framework\DB::db_free_result()` | `common/framework/DB.php:1468` | 2.0 | `$stmt->closeCursor()` | 2.0.0에서 표시 |
| `Rhymix\Framework\DB::db_insert_id()` | `common/framework/DB.php:1480` | 2.0 | `$db->getInsertID()` | 2.0.0에서 표시 |
| `Rhymix\Framework\DB::getSupportedList()` | `common/framework/DB.php:1491` | 2.0 | 없음 | MySQL(PDO)만 지원; 2.0.0에서 표시; 코어 호출 있음 |
| `Rhymix\Framework\DB::getEnableList()` | `common/framework/DB.php:1507` | 2.0 | 없음 | MySQL(PDO)만 지원; 2.0.0에서 표시 |
| `Rhymix\Framework\DB::getDisableList()` | `common/framework/DB.php:1520` | 2.0 | 없음 | MySQL(PDO)만 지원; 2.0.0에서 표시 |
| `Rhymix\Framework\DB::isSupported()` | `common/framework/DB.php:1533` | 2.0 | 없음 | 항상 true; 2.0.0에서 표시; 코어 호출 있음 |
| `Rhymix\Framework\DB::isConnected()` | `common/framework/DB.php:1544` | 2.0 | 없음 | DB::getInstance()가 필요 시 연결; 2.0.0에서 표시 |
| `Rhymix\Framework\DB::close()` | `common/framework/DB.php:1555` | 2.0 | 없음 | 연결은 요청 종료 시 정리, 항상 true; 2.0.0에서 표시; 코어 호출 있음 |
| `Rhymix\Framework\DB::createTableByXmlFile()` | `common/framework/DB.php:1566` | 2.0 | `$db->createTable($filename)` | 2.0.0에서 표시 |
| `Rhymix\Framework\DB::getCountCache()` | `common/framework/DB.php:1588` | 2.0 | 없음 | 클릭 카운트 캐시 기능 제거, 항상 false; 2.0.0에서 표시 |
| `Rhymix\Framework\Filters\MediaFilter::addIframePrefix()` | `common/framework/filters/MediaFilter.php:50` | 1.x | `Rhymix\Framework\Filters\MediaFilter::addPrefix()` | 2.0.24에서 표시 |
| `Rhymix\Framework\Filters\MediaFilter::addObjectPrefix()` | `common/framework/filters/MediaFilter.php:63` | 1.x | `Rhymix\Framework\Filters\MediaFilter::addPrefix()` | 2.0.24에서 표시 |
| `Rhymix\Framework\Filters\MediaFilter::getIframeWhitelist()` | `common/framework/filters/MediaFilter.php:219` | 1.x | `Rhymix\Framework\Filters\MediaFilter::getWhitelist()` | 2.0.24에서 표시; 코어 호출 있음 |
| `Rhymix\Framework\Filters\MediaFilter::getIframeWhitelistRegex()` | `common/framework/filters/MediaFilter.php:230` | 1.x | `Rhymix\Framework\Filters\MediaFilter::getWhitelistRegex()` | 2.0.24에서 표시 |
| `Rhymix\Framework\Filters\MediaFilter::matchIframeWhitelist()` | `common/framework/filters/MediaFilter.php:241` | 1.x | `Rhymix\Framework\Filters\MediaFilter::matchWhitelist()` | 2.0.24에서 표시; 코어 호출 있음 |
| `Rhymix\Framework\Filters\MediaFilter::getObjectWhitelist()` | `common/framework/filters/MediaFilter.php:253` | 1.x | `Rhymix\Framework\Filters\MediaFilter::getWhitelist()` | 2.0.24에서 표시; 코어 호출 있음 |
| `Rhymix\Framework\Filters\MediaFilter::getObjectWhitelistRegex()` | `common/framework/filters/MediaFilter.php:264` | 1.x | `Rhymix\Framework\Filters\MediaFilter::getWhitelistRegex()` | 2.0.24에서 표시 |
| `Rhymix\Framework\Filters\MediaFilter::matchObjectWhitelist()` | `common/framework/filters/MediaFilter.php:275` | 1.x | `Rhymix\Framework\Filters\MediaFilter::matchWhitelist()` | 2.0.24에서 표시; 코어 호출 있음 |

## common/functions.php

| 심볼 | 위치 | 유래 | 대체 API | 비고 |
|---|---|---|---|---|
| `countobj()` | `common/functions.php:594` | 1.x | `count()` | 객체는 count(get_object_vars($obj)); 2.0.24에서 표시; 코어 호출 있음 |

## common/legacy.php

| 심볼 | 위치 | 유래 | 대체 API | 비고 |
|---|---|---|---|---|
| `handleError()` | `common/legacy.php:1263` | XE | `Rhymix\Framework\Debug::addError()` | 2.0.24에서 표시 |
| `getScriptPath()` | `common/legacy.php:1290` | XE | `RX_BASEURL 상수` | 2.0.24에서 표시 |
| `getRequestUriByServerEnviroment()` | `common/legacy.php:1301` | XE | `Context::getRequestUrl()` | 원본 REQUEST_URI가 필요하면 $_SERVER['REQUEST_URI']; 2.0.24에서 표시; 코어 호출 있음 |
| `json_encode2()` | `common/legacy.php:1312` | XE | `json_encode()` | 2.0.24에서 표시 |
| `url_decode()` | `common/legacy.php:1324` | XE | `escape(rawurldecode($str))` | JS escape()의 %uXXXX 형식은 별도 변환 필요; 2.0.24에서 표시 |
| `blockWidgetCode()` | `common/legacy.php:1336` | XE | `Rhymix\Framework\Filters\HTMLFilter::clean($content)` | $allow_widgets=false(기본)면 위젯 코드 제거; 2.0.24에서 표시 |
| `purifierHtml()` | `common/legacy.php:1348` | XE | `Rhymix\Framework\Filters\HTMLFilter::clean()` | 2.0.24에서 표시 |
| `checkXmpTag()` | `common/legacy.php:1360` | XE | 없음 | no-op; 2.0.24에서 표시 |
| `removeSrcHack()` | `common/legacy.php:1370` | XE | 없음 | no-op. XSS 정화는 HTMLFilter::clean(); 2.0.24에서 표시 |
| `checkUploadedFile()` | `common/legacy.php:1382` | XE | `Rhymix\Framework\Filters\FileContentFilter::check($file, $filename)` | 현재 항상 true; 2.0.24에서 표시 |
| `mysql_pre4_hash_password()` | `common/legacy.php:1396` | XE | `VendorPass::mysql_old_password($password)` | 2.0.24에서 표시 |
| `utf8RawUrlDecode()` | `common/legacy.php:1446` | XE | `rawurldecode()` | JS escape()의 %uXXXX는 별도 변환 필요; 2.0.24에서 표시; 코어 호출 있음 |
| `_code2utf()` | `common/legacy.php:1460` | XE | `mb_chr($num, 'UTF-8')` | 2.0.24에서 표시 |
| `writeSlowlog()` | `common/legacy.php:1470` | XE | 없음 | no-op; 2.0.24에서 표시 |
| `flushSlowlog()` | `common/legacy.php:1478` | XE | 없음 | no-op; 2.0.24에서 표시 |
| `requirePear()` | `common/legacy.php:1486` | XE | 없음 | no-op; 2.0.24에서 표시 |

## modules/board/

| 심볼 | 위치 | 유래 | 대체 API | 비고 |
|---|---|---|---|---|
| `BoardView::alertMessage()` | `modules/board/board.view.php:1653` | XE | `throw new Rhymix\Framework\Exceptions\InvalidRequest 등 예외` | View에서 예외를 던지면 에러 화면으로 처리; 2.0.24에서 표시; 코어 호출 있음 |

## modules/comment/

| 심볼 | 위치 | 유래 | 대체 API | 비고 |
|---|---|---|---|---|
| `CommentModel::getDistinctModules()` | `modules/comment/comment.model.php:383` | XE | 없음 | 항상 빈 배열; 2.0.0에서 표시; 코어 호출 있음 |

## modules/counter/

| 심볼 | 위치 | 유래 | 대체 API | 비고 |
|---|---|---|---|---|
| `counterController::insertTodayStatus()` | `modules/counter/counter.controller.php:110` | XE | `CounterController::insertUniqueVisitor()` | 2.0.24에서 표시 |
| `counterController::insertTotalStatus()` | `modules/counter/counter.controller.php:118` | XE | 없음 | no-op; 2.0.24에서 표시 |
| `counterController::deleteSiteCounterLogs()` | `modules/counter/counter.controller.php:126` | XE | 없음 | no-op; 2.0.24에서 표시 |
| `counterModel::isInsertedTodayStatus()` | `modules/counter/counter.model.php:49` | XE | 없음 | no-op; 2.0.24에서 표시 |

## modules/document/

| 심볼 | 위치 | 유래 | 대체 API | 비고 |
|---|---|---|---|---|
| `DocumentItem::getTrackbackUrl()` | `modules/document/document.item.php:865` | XE | 없음 | 트랙백 기능 제거, no-op; 2.0.24에서 표시 |

## modules/file/

| 심볼 | 위치 | 유래 | 대체 API | 비고 |
|---|---|---|---|---|
| `FileAdminController::deleteModuleFiles()` | `modules/file/file.admin.controller.php:18` | XE | `FileController::deleteModuleFiles($module_srl)` | move to fileController; 2.0.0에서 표시; 코어 호출 있음 |

## modules/member/

| 심볼 | 위치 | 유래 | 대체 API | 비고 |
|---|---|---|---|---|
| `MemberController::procMemberSiteSignUp()` | `modules/member/member.controller.php:2235` | XE | 없음 | 가상 사이트 제거, no-op; 2.0.24에서 표시 |
| `MemberController::procMemberSiteLeave()` | `modules/member/member.controller.php:2246` | XE | 없음 | 가상 사이트 제거, no-op; 2.0.24에서 표시 |
| `MemberController::setMemberConfig()` | `modules/member/member.controller.php:2257` | XE | `ModuleController::updateModuleConfig('member', $args)` | 2.0.24에서 표시 |
| `MemberController::_clearMemberCache()` | `modules/member/member.controller.php:4366` | XE | `MemberController::clearMemberCache($member_srl)` | 2.0.24에서 표시 |
| `MemberModel::getApiGroups()` | `modules/member/member.model.php:777` | XE | `MemberModel::getGroups()` | 2.0.0에서 표시 |

## modules/module/

| 심볼 | 위치 | 유래 | 대체 API | 비고 |
|---|---|---|---|---|
| `ModuleModel::getModuleExtend()` | `modules/module/module.model.php:889` | XE | 없음 | module extend 기능 제거; 2.0.0에서 표시 |
| `ModuleModel::loadModuleExtends()` | `modules/module/module.model.php:899` | XE | 없음 | module extend 기능 제거; 2.0.0에서 표시 |

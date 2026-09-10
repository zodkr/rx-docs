<!-- rx-docs tools 브랜치의 deprecated/generate.py 가 생성. 직접 수정 금지. 대체 API는 같은 브랜치의 deprecated/overrides.json 에서 고친다. -->
# Rhymix 2.0.x에서 deprecated 처리된 API

검증 기준: Rhymix 2.1.36, 커밋 `1ae6ce181`, 2026-09-02. 규칙과 열 설명은 [README.md](README.md). 항목 수: 60.

## classes/

| 심볼 | 위치 | 유래 | 대체 API | 비고 |
|---|---|---|---|---|
| `Context::addSSLAction()` | `classes/context/Context.class.php:2115` | XE | 확인 필요 | 2.0.0에서 표시 |
| `Context::addSSLActions()` | `classes/context/Context.class.php:2127` | XE | 확인 필요 | 2.0.0에서 표시 |
| `Context::subtractSSLAction()` | `classes/context/Context.class.php:2139` | XE | 확인 필요 | 2.0.0에서 표시 |
| `Context::getSSLActions()` | `classes/context/Context.class.php:2151` | XE | 확인 필요 | 2.0.0에서 표시 |
| `Context::isExistsSSLAction()` | `classes/context/Context.class.php:2162` | XE | 확인 필요 | 2.0.0에서 표시 |
| `Context::getBodyClass()` | `classes/context/Context.class.php:2622` | XE | 확인 필요 | 2.0.24에서 표시 |
| `FileHandler::clearStatCache()` | `classes/file/FileHandler.class.php:934` | 2.0 | 확인 필요 | 2.0.0에서 표시; 코어 호출 있음 |
| `FileHandler::invalidateOpcache()` | `classes/file/FileHandler.class.php:957` | 2.0 | 확인 필요 | 2.0.0에서 표시; 코어 호출 있음 |

## common/framework/

| 심볼 | 위치 | 유래 | 대체 API | 비고 |
|---|---|---|---|---|
| `Rhymix\Framework\DB::create()` | `common/framework/DB.php:1445` | 2.0 | `DB::getInstance()` | 2.0.0에서 표시; 코어 호출 있음 |
| `Rhymix\Framework\DB::db_fetch_object()` | `common/framework/DB.php:1456` | 2.0 | `$stmt->fetchObject()` | 2.0.0에서 표시 |
| `Rhymix\Framework\DB::db_free_result()` | `common/framework/DB.php:1468` | 2.0 | `$stmt->closeCursor()` | 2.0.0에서 표시 |
| `Rhymix\Framework\DB::db_insert_id()` | `common/framework/DB.php:1480` | 2.0 | `$db->getInsertID()` | 2.0.0에서 표시 |
| `Rhymix\Framework\DB::getSupportedList()` | `common/framework/DB.php:1491` | 2.0 | 확인 필요 | 2.0.0에서 표시; 코어 호출 있음 |
| `Rhymix\Framework\DB::getEnableList()` | `common/framework/DB.php:1507` | 2.0 | 확인 필요 | 2.0.0에서 표시 |
| `Rhymix\Framework\DB::getDisableList()` | `common/framework/DB.php:1520` | 2.0 | 확인 필요 | 2.0.0에서 표시 |
| `Rhymix\Framework\DB::isSupported()` | `common/framework/DB.php:1533` | 2.0 | 확인 필요 | 2.0.0에서 표시; 코어 호출 있음 |
| `Rhymix\Framework\DB::isConnected()` | `common/framework/DB.php:1544` | 2.0 | 확인 필요 | 2.0.0에서 표시 |
| `Rhymix\Framework\DB::close()` | `common/framework/DB.php:1555` | 2.0 | 확인 필요 | 2.0.0에서 표시; 코어 호출 있음 |
| `Rhymix\Framework\DB::createTableByXmlFile()` | `common/framework/DB.php:1566` | 2.0 | `$db->createTable($filename)` | 2.0.0에서 표시 |
| `Rhymix\Framework\DB::getCountCache()` | `common/framework/DB.php:1588` | 2.0 | 확인 필요 | 2.0.0에서 표시 |
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
| `countobj()` | `common/functions.php:594` | 1.x | 확인 필요 | 2.0.24에서 표시; 코어 호출 있음 |

## common/legacy.php

| 심볼 | 위치 | 유래 | 대체 API | 비고 |
|---|---|---|---|---|
| `handleError()` | `common/legacy.php:1263` | XE | `Rhymix\Framework\Debug::addError()` | 2.0.24에서 표시 |
| `getScriptPath()` | `common/legacy.php:1290` | XE | 확인 필요 | 2.0.24에서 표시 |
| `getRequestUriByServerEnviroment()` | `common/legacy.php:1301` | XE | 확인 필요 | 2.0.24에서 표시; 코어 호출 있음 |
| `json_encode2()` | `common/legacy.php:1312` | XE | 확인 필요 | 2.0.24에서 표시 |
| `url_decode()` | `common/legacy.php:1324` | XE | 확인 필요 | 2.0.24에서 표시 |
| `blockWidgetCode()` | `common/legacy.php:1336` | XE | 확인 필요 | 2.0.24에서 표시 |
| `purifierHtml()` | `common/legacy.php:1348` | XE | `Rhymix\Framework\Filters\HTMLFilter::clean()` | 2.0.24에서 표시 |
| `checkXmpTag()` | `common/legacy.php:1360` | XE | 확인 필요 | 2.0.24에서 표시 |
| `removeSrcHack()` | `common/legacy.php:1370` | XE | 확인 필요 | 2.0.24에서 표시 |
| `checkUploadedFile()` | `common/legacy.php:1382` | XE | 확인 필요 | 2.0.24에서 표시 |
| `mysql_pre4_hash_password()` | `common/legacy.php:1396` | XE | 확인 필요 | 2.0.24에서 표시 |
| `utf8RawUrlDecode()` | `common/legacy.php:1446` | XE | 확인 필요 | 2.0.24에서 표시; 코어 호출 있음 |
| `_code2utf()` | `common/legacy.php:1460` | XE | 확인 필요 | 2.0.24에서 표시 |
| `writeSlowlog()` | `common/legacy.php:1470` | XE | 확인 필요 | 2.0.24에서 표시 |
| `flushSlowlog()` | `common/legacy.php:1478` | XE | 확인 필요 | 2.0.24에서 표시 |
| `requirePear()` | `common/legacy.php:1486` | XE | 확인 필요 | 2.0.24에서 표시 |

## modules/board/

| 심볼 | 위치 | 유래 | 대체 API | 비고 |
|---|---|---|---|---|
| `BoardView::alertMessage()` | `modules/board/board.view.php:1653` | XE | 확인 필요 | 2.0.24에서 표시; 코어 호출 있음 |

## modules/comment/

| 심볼 | 위치 | 유래 | 대체 API | 비고 |
|---|---|---|---|---|
| `CommentModel::getDistinctModules()` | `modules/comment/comment.model.php:383` | XE | 확인 필요 | 2.0.0에서 표시; 코어 호출 있음 |

## modules/counter/

| 심볼 | 위치 | 유래 | 대체 API | 비고 |
|---|---|---|---|---|
| `counterController::insertTodayStatus()` | `modules/counter/counter.controller.php:110` | XE | 확인 필요 | 2.0.24에서 표시 |
| `counterController::insertTotalStatus()` | `modules/counter/counter.controller.php:118` | XE | 확인 필요 | 2.0.24에서 표시 |
| `counterController::deleteSiteCounterLogs()` | `modules/counter/counter.controller.php:126` | XE | 확인 필요 | 2.0.24에서 표시 |
| `counterModel::isInsertedTodayStatus()` | `modules/counter/counter.model.php:49` | XE | 확인 필요 | 2.0.24에서 표시 |

## modules/document/

| 심볼 | 위치 | 유래 | 대체 API | 비고 |
|---|---|---|---|---|
| `DocumentItem::getTrackbackUrl()` | `modules/document/document.item.php:865` | XE | 확인 필요 | 2.0.24에서 표시 |

## modules/file/

| 심볼 | 위치 | 유래 | 대체 API | 비고 |
|---|---|---|---|---|
| `FileAdminController::deleteModuleFiles()` | `modules/file/file.admin.controller.php:18` | XE | 확인 필요 | move to fileController; 2.0.0에서 표시; 코어 호출 있음 |

## modules/member/

| 심볼 | 위치 | 유래 | 대체 API | 비고 |
|---|---|---|---|---|
| `MemberController::procMemberSiteSignUp()` | `modules/member/member.controller.php:2235` | XE | 확인 필요 | 2.0.24에서 표시 |
| `MemberController::procMemberSiteLeave()` | `modules/member/member.controller.php:2246` | XE | 확인 필요 | 2.0.24에서 표시 |
| `MemberController::setMemberConfig()` | `modules/member/member.controller.php:2257` | XE | 확인 필요 | 2.0.24에서 표시 |
| `MemberController::_clearMemberCache()` | `modules/member/member.controller.php:4366` | XE | 확인 필요 | 2.0.24에서 표시 |
| `MemberModel::getApiGroups()` | `modules/member/member.model.php:777` | XE | 확인 필요 | 2.0.0에서 표시 |

## modules/module/

| 심볼 | 위치 | 유래 | 대체 API | 비고 |
|---|---|---|---|---|
| `ModuleModel::getModuleExtend()` | `modules/module/module.model.php:889` | XE | 확인 필요 | 2.0.0에서 표시 |
| `ModuleModel::loadModuleExtends()` | `modules/module/module.model.php:899` | XE | 확인 필요 | 2.0.0에서 표시 |

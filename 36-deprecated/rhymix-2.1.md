<!-- rx-docs tools 브랜치의 deprecated/generate.py 가 생성. 직접 수정 금지. 대체 API는 같은 브랜치의 deprecated/overrides.json 에서 고친다. -->
# Rhymix 2.1.x에서 deprecated 처리된 API

검증 기준: Rhymix 2.1.36, 커밋 `1ae6ce181`, 2026-09-02. 규칙과 열 설명은 [README.md](README.md). 항목 수: 93.

## classes/

| 심볼 | 위치 | 유래 | 대체 API | 비고 |
|---|---|---|---|---|
| `Context::getDBType()` | `classes/context/Context.class.php:551` | XE | `config('db.master.type')` |  |
| `Context::setDBInfo()` | `classes/context/Context.class.php:562` | XE | 확인 필요 |  |
| `Context::getDBInfo()` | `classes/context/Context.class.php:574` | XE | `config('db.master')` | `Rhymix\Framework\Config::get('db')`와 동일; 코어 호출 있음 |
| `Context::getRouteInfo()` | `classes/context/Context.class.php:585` | 2.0 | 확인 필요 |  |
| `Context::getSSLStatus()` | `classes/context/Context.class.php:606` | XE | `Context::get('_use_ssl')` | `RX_SSL` 상수도 참고; 코어 호출 있음 |
| `Context::checkSSO()` | `classes/context/Context.class.php:681` | XE | 확인 필요 |  |
| `Context::isFTPRegisted()` | `classes/context/Context.class.php:692` | XE | 확인 필요 |  |
| `Context::getFTPInfo()` | `classes/context/Context.class.php:704` | XE | 확인 필요 |  |
| `Context::convertEncoding()` | `classes/context/Context.class.php:980` | XE | 확인 필요 | 2.1.0에서 표시; 코어 호출 있음 |
| `Context::checkConvertFlag()` | `classes/context/Context.class.php:1018` | XE | 확인 필요 | 2.1.0에서 표시; 코어 호출 있음 |
| `Context::doConvertEncoding()` | `classes/context/Context.class.php:1047` | XE | 확인 필요 | 2.1.0에서 표시 |
| `Context::convertEncodingStr()` | `classes/context/Context.class.php:1070` | XE | 확인 필요 | 2.1.0에서 표시; 코어 호출 있음 |
| `Context::encodeIdna()` | `classes/context/Context.class.php:1091` | 1.x | `Rhymix\Framework\URL::encodeIdna()` | 코어 호출 있음 |
| `Context::decodeIdna()` | `classes/context/Context.class.php:1103` | XE | `Rhymix\Framework\URL::decodeIdna()` | 코어 호출 있음 |
| `Context::isUploaded()` | `classes/context/Context.class.php:1560` | XE | 확인 필요 | 코어 호출 있음 |
| `Context::_setUploadedArgument()` | `classes/context/Context.class.php:1571` | XE | 확인 필요 |  |
| `Context::getJSCallbackFunc()` | `classes/context/Context.class.php:1706` | XE | 확인 필요 | 코어 호출 있음 |
| `Context::getConfigFile()` | `classes/context/Context.class.php:2720` | XE | 확인 필요 |  |
| `Context::getFTPConfigFile()` | `classes/context/Context.class.php:2731` | XE | 확인 필요 |  |
| `Context::transContent()` | `classes/context/Context.class.php:2778` | XE | 없음 | no-op, 인자를 그대로 반환 |
| `Context::isAllowRewrite()` | `classes/context/Context.class.php:2790` | XE | `Rhymix\Framework\Router::getRewriteLevel()` | 코어 호출 있음 |
| `Context::pathToUrl()` | `classes/context/Context.class.php:2877` | XE | `Rhymix\Framework\URL::fromServerPath(FileHandler::getRealPath($path))` | 원본은 루트 상대 경로, 대체는 절대 URL(문서 루트 밖이면 false). 의미 차이 확인; 코어 호출 있음 |
| `FileHandler::readIniFile()` | `classes/file/FileHandler.class.php:790` | XE | 확인 필요 | 코어 호출 있음 |
| `FileHandler::writeIniFile()` | `classes/file/FileHandler.class.php:816` | XE | 확인 필요 | 코어 호출 있음 |
| `FileHandler::_makeIniBuff()` | `classes/file/FileHandler.class.php:835` | XE | 확인 필요 | 코어 호출 있음 |
| `FileHandler::openFile()` | `classes/file/FileHandler.class.php:872` | XE | 확인 필요 | 코어 호출 있음 |
| `Mobile::_isFromMobilePhone()` | `classes/mobile/Mobile.class.php:84` | XE | `Mobile::isFromMobilePhone()` |  |
| `Mobile::isMobileCheckByAgent()` | `classes/mobile/Mobile.class.php:95` | XE | `Rhymix\Framework\UA::isMobile()` |  |
| `Mobile::isMobilePadCheckByAgent()` | `classes/mobile/Mobile.class.php:106` | XE | `Rhymix\Framework\UA::isTablet()` |  |
| `Mobile::setMobile()` | `classes/mobile/Mobile.class.php:117` | XE | 확인 필요 | 코어 호출 있음 |
| `ModuleObject::setRefreshPage()` | `classes/module/ModuleObject.class.php:166` | XE | 확인 필요 | 2.1.0에서 표시; 코어 호출 있음 |
| `class EmbedFilter` | `classes/security/EmbedFilter.class.php:4` | XE | `Rhymix\Framework\Filters\MediaFilter` | 동명 `Rhymix\Framework` 클래스와 이름 충돌 |
| `class IpFilter` | `classes/security/IpFilter.class.php:4` | XE | `Rhymix\Framework\Filters\IpFilter` | 동명 `Rhymix\Framework` 클래스와 이름 충돌 |
| `class Password` | `classes/security/Password.class.php:4` | XE | `Rhymix\Framework\Password` | 동명 `Rhymix\Framework` 클래스와 이름 충돌 |
| `class Purifier` | `classes/security/Purifier.class.php:4` | XE | `Rhymix\Framework\Filters\HTMLFilter` | 동명 `Rhymix\Framework` 클래스와 이름 충돌 |
| `class Security` | `classes/security/Security.class.php:6` | XE | `Rhymix\Framework\Security` | 동명 `Rhymix\Framework` 클래스와 이름 충돌 |
| `class XeXmlParser` | `classes/xml/XmlParser.class.php:8` | 2.0 | `Rhymix\Framework\Parsers\XEXMLParser` | `XmlParser`는 이 클래스의 class_alias |
| `XeXmlParser::loadXmlFile()` | `classes/xml/XmlParser.class.php:15` | 2.0 | `Rhymix\Framework\Parsers\XEXMLParser::loadXMLFile()` | 코어 호출 있음 |
| `XeXmlParser::parse()` | `classes/xml/XmlParser.class.php:35` | 2.0 | `Rhymix\Framework\Parsers\XEXMLParser::loadXMLString()` | 코어 호출 있음 |

## common/framework/

| 심볼 | 위치 | 유래 | 대체 API | 비고 |
|---|---|---|---|---|
| `Rhymix\Framework\DB::_query()` | `common/framework/DB.php:1409` | 2.0 | `query()` | 2.1.0에서 표시 |
| `Rhymix\Framework\DB::_fetch()` | `common/framework/DB.php:1431` | 2.0 | 추정: `$this->fetch()` | 2.1.0에서 표시 |
| `Rhymix\Framework\Formatter::convertIECondition()` | `common/framework/Formatter.php:564` | 1.x | 확인 필요 | 2.1.0에서 표시 |

## common/legacy.php

| 심볼 | 위치 | 유래 | 대체 API | 비고 |
|---|---|---|---|---|
| `getWAP()` | `common/legacy.php:163` | XE | 확인 필요 | 2.1.0에서 표시 |
| `setUserSequence()` | `common/legacy.php:235` | XE | 없음 | getNextSequence()가 내부에서 호출; 코어 호출 있음 |
| `checkUserSequence()` | `common/legacy.php:256` | XE | 없음 | 코어 호출 있음 |
| `getAutoEncodedUrl()` | `common/legacy.php:322` | XE | `getUrl(...)` |  |
| `getSiteUrl()` | `common/legacy.php:396` | XE | `Context::getUrl(..., $domain)` | $domain은 사이트 정보 객체가 아닌 도메인 문자열. 객체를 넘기면 PHP 8에서 TypeError; 코어 호출 있음 |
| `getNotEncodedSiteUrl()` | `common/legacy.php:419` | XE | `Context::getUrl(..., $domain)` | 네 번째 인자 false(HTML 이스케이프 없음)와 동일. $domain은 도메인 문자열; 코어 호출 있음 |
| `getFullSiteUrl()` | `common/legacy.php:441` | XE | `Context::getUrl(..., $domain)` | $domain은 도메인 문자열; 코어 호출 있음 |
| `isSiteID()` | `common/legacy.php:481` | XE | 확인 필요 |  |
| `get_time_zone_offset()` | `common/legacy.php:554` | 1.x | `Rhymix\Framework\DateTime::getTimezoneOffsetByLegacyFormat()` |  |
| `getEncodeEmailAddress()` | `common/legacy.php:787` | XE | 없음 |  |
| `delObjectVars()` | `common/legacy.php:821` | XE | 없음 | 코어 호출 있음 |
| `getDestroyXeVars()` | `common/legacy.php:844` | XE | 없음 | 코어 호출 있음 |
| `removeHackTag()` | `common/legacy.php:891` | XE | `Rhymix\Framework\Filters\HTMLFilter::clean()` | 코어 호출 있음 |
| `detectUTF8()` | `common/legacy.php:903` | XE | `utf8_check()` | $return_convert 변환 경로의 대체는 확인 필요 |
| `stripEmbedTagForAdmin()` | `common/legacy.php:942` | XE | `Rhymix\Framework\Filters\MediaFilter::removeEmbeddedMedia($content, $msg)` | 관리자/작성자 판정은 호출부에서 수행; 코어 호출 있음 |
| `checkCSRF()` | `common/legacy.php:985` | XE | `Rhymix\Framework\Security::checkCSRF()` | 코어 호출 있음 |
| `recurciveExposureCheck()` | `common/legacy.php:996` | XE | 확인 필요 | 코어 호출 있음 |
| `hexrgb()` | `common/legacy.php:1022` | XE | 확인 필요 |  |
| `htmlHeader()` | `common/legacy.php:1202` | XE | 확인 필요 | 코어 호출 있음 |
| `htmlFooter()` | `common/legacy.php:1213` | XE | 확인 필요 | 코어 호출 있음 |
| `alertScript()` | `common/legacy.php:1224` | XE | 확인 필요 | 코어 호출 있음 |
| `closePopupScript()` | `common/legacy.php:1239` | XE | 확인 필요 | 코어 호출 있음 |
| `reload()` | `common/legacy.php:1250` | XE | 확인 필요 | 코어 호출 있음 |
| `getMicroTime()` | `common/legacy.php:1279` | XE | 확인 필요 |  |
| `changeValueInUrl()` | `common/legacy.php:1408` | XE | 확인 필요 | 코어 호출 있음 |

## common/scripts/

| 심볼 | 위치 | 유래 | 대체 API | 비고 |
|---|---|---|---|---|
| `file common/scripts/clean_empty_dirs.php` | `common/scripts/clean_empty_dirs.php:4` | 1.x | `php index.php file.cleanEmptyDirs` | . |
| `file common/scripts/clean_garbage_files.php` | `common/scripts/clean_garbage_files.php:4` | 1.x | `php index.php file.cleanGarbageFiles` | . |
| `file common/scripts/clean_message_files.php` | `common/scripts/clean_message_files.php:4` | 2.0 | `php index.php communication.cleanMessageFiles` | . |
| `file common/scripts/clean_old_logs.php` | `common/scripts/clean_old_logs.php:4` | 2.0 | `php index.php module.cleanMiscLogs` | . |
| `file common/scripts/clean_old_notifications.php` | `common/scripts/clean_old_notifications.php:4` | 1.x | `php index.php ncenterlite.cleanNotifications` | . |
| `file common/scripts/clean_old_thumbnails.php` | `common/scripts/clean_old_thumbnails.php:4` | 1.x | `php index.php file.cleanThumbnails` | . |
| `file common/scripts/update_all_modules.php` | `common/scripts/update_all_modules.php:4` | 2.0 | `php index.php module.updateAllModules` | . |

## modules/admin/

| 심볼 | 위치 | 유래 | 대체 API | 비고 |
|---|---|---|---|---|
| `class AdminAdminController` | `modules/admin/admin.admin.controller.php:6` | XE | `Rhymix\Modules\Admin\Controllers\*` | 2.1.0에서 표시 |
| `AdminAdminController::procAdminDeleteLogo()` | `modules/admin/admin.admin.controller.php:24` | XE | 확인 필요 | 2.1.0에서 표시 |
| `class AdminAdminModel` | `modules/admin/admin.admin.model.php:6` | XE | `Rhymix\Modules\Admin\Controllers\*` | 2.1.0에서 표시 |
| `class AdminAdminView` | `modules/admin/admin.admin.view.php:6` | XE | `Rhymix\Modules\Admin\Controllers\*` | 2.1.0에서 표시 |
| `AdminAdminView::makeGnbUrl()` | `modules/admin/admin.admin.view.php:13` | XE | 확인 필요 | 2.1.0에서 표시 |
| `AdminAdminView::dispAdminConfigFtp()` | `modules/admin/admin.admin.view.php:23` | XE | 확인 필요 | 2.1.0에서 표시 |
| `Rhymix\Modules\Admin\Controllers\Base::getAdminMenuName()` | `modules/admin/controllers/Base.php:171` | 2.1 | 확인 필요 | 2.1.0에서 표시; 코어 호출 있음 |
| `Rhymix\Modules\Admin\Controllers\Base::getAdminMenuLang()` | `modules/admin/controllers/Base.php:181` | 2.1 | 확인 필요 | 2.1.0에서 표시; 코어 호출 있음 |

## modules/document/

| 심볼 | 위치 | 유래 | 대체 API | 비고 |
|---|---|---|---|---|
| `DocumentController::updateUploaedCount()` | `modules/document/document.controller.php:3889` | XE | 추정: `$this->updateUploadedCount()` |  |
| `DocumentItem::_addAllowScriptAccess()` | `modules/document/document.item.php:669` | XE | 확인 필요 |  |
| `DocumentItem::_checkAllowScriptAccess()` | `modules/document/document.item.php:682` | XE | 확인 필요 |  |

## modules/extravar/

| 심볼 | 위치 | 유래 | 대체 API | 비고 |
|---|---|---|---|---|
| `Rhymix\Modules\Extravar\Models\ValueCollection::getInstance()` | `modules/extravar/models/ValueCollection.php:17` | 2.1 | 확인 필요 | 코어 호출 있음 |

## modules/file/

| 심볼 | 위치 | 유래 | 대체 API | 비고 |
|---|---|---|---|---|
| `FileController::procFileImageResize()` | `modules/file/file.controller.php:272` | XE | 확인 필요 |  |
| `FileModel::getFileModuleConfig()` | `modules/file/file.model.php:557` | XE | 추정: `self::getFileConfig()` | 2.1.0에서 표시 |
| `FileModel::getFileGrant()` | `modules/file/file.model.php:567` | XE | 추정: `self::isDeletable()` | 2.1.0에서 표시 |

## modules/integration_search/

| 심볼 | 위치 | 유래 | 대체 API | 비고 |
|---|---|---|---|---|
| `integration_searchModel::getTrackbacks()` | `modules/integration_search/integration_search.model.php:281` | XE | 확인 필요 |  |

## modules/module/

| 심볼 | 위치 | 유래 | 대체 API | 비고 |
|---|---|---|---|---|
| `ModuleController::updateModuleSite()` | `modules/module/module.controller.php:622` | XE | 확인 필요 | 2.1.0에서 표시 |
| `ModuleController::updateModuleMenu()` | `modules/module/module.controller.php:762` | XE | 확인 필요 |  |
| `ModuleController::updateModuleInSites()` | `modules/module/module.controller.php:1363` | XE | 확인 필요 | 2.1.0에서 표시 |

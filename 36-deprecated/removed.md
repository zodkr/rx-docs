<!-- rx-docs tools 브랜치의 deprecated/generate.py 가 생성. 직접 수정 금지. 대체 API는 같은 브랜치의 deprecated/overrides.json 에서 고친다. -->
# `@deprecated` 표시 없이 삭제된 공개 API

검증 기준: Rhymix 2.1.36, 커밋 `1ae6ce181`, 2026-09-02. 규칙과 열 설명은 [README.md](README.md). 항목 수: 37.

삭제된 API는 호출 즉시 fatal error가 난다. 발견 즉시 대체 API로 바꾼다. 마지막 존재 열은 `태그 경로:줄`이며, 제거 시점은 그 다음 릴리스 태그 기준이다.

## Rhymix 1.x에서 삭제됨

| 심볼 | 마지막 존재 | 대체 API | 비고 |
|---|---|---|---|
| `editorModel::getDrComponentXmlInfo()` | `1.8.0 modules/editor/editor.model.php:116` | 확인 필요 |  |
| `editorModel::loadDrComponents()` | `1.8.0 modules/editor/editor.model.php:93` | 확인 필요 |  |
| `memberController::procMemberUpdateAuthMail()` | `1.8.0 modules/member/member.controller.php:1169` | 확인 필요 |  |
| `moduleController::insertSiteAdmin()` | `1.8.0 modules/module/module.controller.php:829` | 확인 필요 |  |

## Rhymix 2.0에서 삭제됨

| 심볼 | 마지막 존재 | 대체 API | 비고 |
|---|---|---|---|
| `class XmlQueryParser` | `1.9.13 classes/xml/XmlQueryParser.class.php:45` | 확인 필요 |  |
| `class SFTPModuleInstaller` | `1.9.0 modules/autoinstall/autoinstall.lib.php:320` | 확인 필요 |  |
| `class PHPFTPModuleInstaller` | `1.9.0 modules/autoinstall/autoinstall.lib.php:489` | 확인 필요 |  |
| `class FTPModuleInstaller` | `1.9.0 modules/autoinstall/autoinstall.lib.php:703` | 확인 필요 |  |
| `boardAdminController::procBoardAdminUpdateBoardFroBasic()` | `1.9.13 modules/board/board.admin.controller.php:101` | 확인 필요 |  |
| `editorModel::getCacheFile()` | `1.9.0 modules/editor/editor.model.php:576` | 확인 필요 |  |
| `fileAdminController::procFileAdminInsertConfig()` | `1.9.0 modules/file/file.admin.controller.php:92` | 확인 필요 |  |
| `fileController::triggerCheckAttached()` | `1.9.13 modules/file/file.controller.php:439` | 확인 필요 |  |
| `fileController::triggerAttachFiles()` | `1.9.13 modules/file/file.controller.php:456` | 확인 필요 |  |
| `fileController::triggerCommentCheckAttached()` | `1.9.13 modules/file/file.controller.php:488` | 확인 필요 |  |
| `fileController::triggerCommentAttachFiles()` | `1.9.13 modules/file/file.controller.php:505` | 확인 필요 |  |
| `memberController::procMemberResetAuthMail()` | `1.9.0 modules/member/member.controller.php:1319` | 확인 필요 |  |
| `pointController::triggerUpdateDocument()` | `1.9.13 modules/point/point.controller.php:102` | 확인 필요 |  |
| `spamfilterController::triggerInsertTrackback()` | `1.9.13 modules/spamfilter/spamfilter.controller.php:119` | 확인 필요 |  |

## Rhymix 2.1에서 삭제됨

| 심볼 | 마지막 존재 | 대체 API | 비고 |
|---|---|---|---|
| `class Object` | `2.0.24 classes/object/Object.class.php:9` | `BaseObject` | PHP 7.2 예약어. 2.0.24까지 PHP<7.2에서만 alias, 현재 없음 |
| `class Xml_Node_` | `2.1.0 classes/xml/XmlParser.class.php:11` | 확인 필요 |  |
| `class Rhymix\Framework\Drivers\Cache\WinCache` | `2.0.24 common/framework/drivers/cache/wincache.php:8` | 확인 필요 |  |
| `class Rhymix\Framework\Drivers\Cache\XCache` | `2.0.24 common/framework/drivers/cache/xcache.php:8` | 확인 필요 |  |
| `class Rhymix\Framework\Drivers\SMS\ApiStore` | `2.1.0 common/framework/drivers/sms/apistore.php:8` | 확인 필요 |  |
| `class XmlGenerater` | `2.1.0 modules/autoinstall/autoinstall.class.php:8` | 확인 필요 |  |
| `class ModuleInstaller` | `2.1.0 modules/autoinstall/autoinstall.lib.php:10` | 확인 필요 |  |
| `class DirectModuleInstaller` | `2.1.0 modules/autoinstall/autoinstall.lib.php:876` | 확인 필요 |  |
| `class autoinstallModel` | `2.1.0 modules/autoinstall/autoinstall.model.php:8` | 확인 필요 |  |
| `class boardWAP` | `2.0.24 modules/board/board.wap.php:10` | 확인 필요 |  |
| `class pageWap` | `2.0.24 modules/page/page.wap.php:8` | 확인 필요 |  |
| `class spamfilter_reCAPTCHA` | `2.0.24 modules/spamfilter/spamfilter.lib.php:3` | 확인 필요 |  |
| `TemplateHandler::resetState()` | `2.1.0 classes/template/TemplateHandler.class.php:72` | 확인 필요 |  |
| `Validator::mbStrLen()` | `2.1.0 classes/validator/Validator.class.php:638` | 확인 필요 |  |
| `Rhymix\Framework\Debug::addSessionStartTime()` | `2.1.0 common/framework/debug.php:252` | 확인 필요 |  |
| `Rhymix\Framework\Session::checkSSO()` | `2.1.0 common/framework/session.php:333` | 확인 필요 |  |
| `layoutAdminModel::getLayoutAdminSetHTMLCSS()` | `2.1.0 modules/layout/layout.admin.model.php:100` | 확인 필요 |  |
| `menuAdminController::procMenuAdminUploadButton()` | `2.1.0 modules/menu/menu.admin.controller.php:1497` | 확인 필요 |  |
| `menuAdminController::procMenuAdminDeleteButton()` | `2.1.0 modules/menu/menu.admin.controller.php:1537` | 확인 필요 |  |

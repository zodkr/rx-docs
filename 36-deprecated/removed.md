<!-- rx-docs tools 브랜치의 deprecated/generate.py 가 생성. 직접 수정 금지. 대체 API는 같은 브랜치의 deprecated/overrides.json 에서 고친다. -->
# `@deprecated` 표시 없이 삭제된 공개 API

검증 기준: Rhymix 2.1.36, 커밋 `1ae6ce181`, 2026-09-02. 규칙과 열 설명은 [README.md](README.md). 항목 수: 37.

삭제된 API는 호출 즉시 fatal error가 난다. 발견 즉시 대체 API로 바꾼다. 마지막 존재 열은 `태그 경로:줄`이며, 제거 시점은 그 다음 릴리스 태그 기준이다.

## Rhymix 1.x에서 삭제됨

| 심볼 | 마지막 존재 | 대체 API | 비고 |
|---|---|---|---|
| `editorModel::getDrComponentXmlInfo()` | `1.8.0 modules/editor/editor.model.php:116` | 없음 | DR 에디터(dreditor) 컴포넌트 제거 |
| `editorModel::loadDrComponents()` | `1.8.0 modules/editor/editor.model.php:93` | 없음 | DR 에디터(dreditor) 컴포넌트 제거 |
| `memberController::procMemberUpdateAuthMail()` | `1.8.0 modules/member/member.controller.php:1169` | `MemberController::procMemberResendAuthMail()` |  |
| `moduleController::insertSiteAdmin()` | `1.8.0 modules/module/module.controller.php:829` | 없음 | 가상 사이트 제거 |

## Rhymix 2.0에서 삭제됨

| 심볼 | 마지막 존재 | 대체 API | 비고 |
|---|---|---|---|
| `class XmlQueryParser` | `1.9.13 classes/xml/XmlQueryParser.class.php:20` | `Rhymix\Framework\Parsers\DBQueryParser` | XML 쿼리는 executeQuery()가 내부에서 파싱·캐시 |
| `class SFTPModuleInstaller` | `1.9.0 modules/autoinstall/autoinstall.lib.php:320` | `Rhymix\Modules\Autoinstall\Models\Installer` | FTP 설치 방식 제거 |
| `class PHPFTPModuleInstaller` | `1.9.0 modules/autoinstall/autoinstall.lib.php:489` | `Rhymix\Modules\Autoinstall\Models\Installer` | FTP 설치 방식 제거 |
| `class FTPModuleInstaller` | `1.9.0 modules/autoinstall/autoinstall.lib.php:703` | `Rhymix\Modules\Autoinstall\Models\Installer` | FTP 설치 방식 제거 |
| `boardAdminController::procBoardAdminUpdateBoardFroBasic()` | `1.9.13 modules/board/board.admin.controller.php:111` | `BoardAdminController::procBoardAdminUpdateBoard()` |  |
| `editorModel::getCacheFile()` | `1.9.0 modules/editor/editor.model.php:494` | 없음 | 컴포넌트 목록은 EditorModel::getComponentList()가 Cache로 관리 |
| `fileAdminController::procFileAdminInsertConfig()` | `1.9.0 modules/file/file.admin.controller.php:92` | `FileAdminController::procFileAdminInsertUploadConfig() / procFileAdminInsertDownloadConfig() / procFileAdminInsertOtherConfig()` |  |
| `fileController::triggerCheckAttached()` | `1.9.13 modules/file/file.controller.php:653` | `FileController::setFilesValid($upload_target_srl, $upload_target_type)` | 문서·댓글 컨트롤러가 직접 호출 |
| `fileController::triggerAttachFiles()` | `1.9.13 modules/file/file.controller.php:670` | `FileController::setFilesValid($upload_target_srl, $upload_target_type)` | 문서·댓글 컨트롤러가 직접 호출 |
| `fileController::triggerCommentCheckAttached()` | `1.9.13 modules/file/file.controller.php:700` | `FileController::setFilesValid($upload_target_srl, $upload_target_type)` | 문서·댓글 컨트롤러가 직접 호출 |
| `fileController::triggerCommentAttachFiles()` | `1.9.13 modules/file/file.controller.php:715` | `FileController::setFilesValid($upload_target_srl, $upload_target_type)` | 문서·댓글 컨트롤러가 직접 호출 |
| `memberController::procMemberResetAuthMail()` | `1.9.0 modules/member/member.controller.php:1596` | `MemberController::procMemberResendAuthMail()` |  |
| `pointController::triggerUpdateDocument()` | `1.9.13 modules/point/point.controller.php:127` | `PointController::triggerBeforeUpdateDocument() / triggerAfterUpdateDocument()` |  |
| `spamfilterController::triggerInsertTrackback()` | `1.9.13 modules/spamfilter/spamfilter.controller.php:117` | 없음 | 트랙백 제거 |

## Rhymix 2.1에서 삭제됨

| 심볼 | 마지막 존재 | 대체 API | 비고 |
|---|---|---|---|
| `class Object` | `2.0.24 classes/object/Object.class.php:10` | `BaseObject` | PHP 7.2 예약어. 2.0.24까지 PHP<7.2에서만 alias, 현재 없음 |
| `class Xml_Node_` | `2.1.0 classes/xml/XmlParser.class.php:11` | `Rhymix\Framework\Parsers\XEXMLParser` | 노드도 XEXMLParser 인스턴스 |
| `class Rhymix\Framework\Drivers\Cache\WinCache` | `2.0.24 common/framework/drivers/cache/wincache.php:8` | `Rhymix\Framework\Drivers\Cache\APC` | PHP 확장 단종. APCu 사용 |
| `class Rhymix\Framework\Drivers\Cache\XCache` | `2.0.24 common/framework/drivers/cache/xcache.php:8` | `Rhymix\Framework\Drivers\Cache\APC` | PHP 확장 단종. APCu 사용 |
| `class Rhymix\Framework\Drivers\SMS\ApiStore` | `2.1.0 common/framework/drivers/sms/apistore.php:8` | 없음 | 서비스 종료. 다른 SMS 드라이버(coolsms, solapi, twilio 등) 사용 |
| `class XmlGenerater` | `2.1.0 modules/autoinstall/autoinstall.class.php:8` | 없음 | XML-RPC 요청 제거. Rhymix\Modules\Autoinstall\Models\Package가 api.rhymix.org JSON API 사용 |
| `class DirectModuleInstaller` | `2.1.0 modules/autoinstall/autoinstall.lib.php:315` | `Rhymix\Modules\Autoinstall\Models\Installer` |  |
| `class ModuleInstaller` | `2.1.0 modules/autoinstall/autoinstall.lib.php:8` | `Rhymix\Modules\Autoinstall\Models\Installer` |  |
| `class autoinstallModel` | `2.1.0 modules/autoinstall/autoinstall.model.php:8` | `AutoinstallAdminModel / Rhymix\Modules\Autoinstall\Models\Package` | 패키지 조회는 Package::getPackage()·searchPackages() |
| `class boardWAP` | `2.0.24 modules/board/board.wap.php:10` | 없음 | WAP 제거. 모바일은 m.skins와 *Mobile 클래스 |
| `class pageWap` | `2.0.24 modules/page/page.wap.php:8` | 없음 | WAP 제거. 모바일은 m.skins와 *Mobile 클래스 |
| `class spamfilter_reCAPTCHA` | `2.0.24 modules/spamfilter/spamfilter.lib.php:3` | `Rhymix\Modules\Spamfilter\Captcha\reCAPTCHA` |  |
| `TemplateHandler::resetState()` | `2.1.0 classes/template/TemplateHandler.class.php:70` | 없음 | 내부 메서드. Template v2로 재작성 |
| `Validator::mbStrLen()` | `2.1.0 classes/validator/Validator.class.php:640` | `mb_strlen($str)` |  |
| `Rhymix\Framework\Debug::addSessionStartTime()` | `2.1.0 common/framework/Debug.php:252` | 없음 | 세션 시간은 Debug 내부 타이머(session)가 측정 |
| `Rhymix\Framework\Session::checkSSO()` | `2.1.0 common/framework/Session.php:323` | 없음 | SSO 제거 |
| `layoutAdminModel::getLayoutAdminSetHTMLCSS()` | `2.1.0 modules/layout/layout.admin.model.php:100` | 없음 | 레이아웃 코드 편집은 LayoutAdminView::dispLayoutAdminEdit() |
| `menuAdminController::procMenuAdminUploadButton()` | `2.1.0 modules/menu/menu.admin.controller.php:1560` | `MenuAdminController::procMenuAdminButtonUpload()` |  |
| `menuAdminController::procMenuAdminDeleteButton()` | `2.1.0 modules/menu/menu.admin.controller.php:1600` | 없음 | 버튼 삭제 액션 제거. 메뉴 항목 수정으로 처리 |

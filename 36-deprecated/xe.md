<!-- rx-docs tools 브랜치의 deprecated/generate.py 가 생성. 직접 수정 금지. 대체 API는 같은 브랜치의 deprecated/overrides.json 에서 고친다. -->
# XE 1.8.0에서 이미 deprecated 처리된 API

검증 기준: Rhymix 2.1.36, 커밋 `1ae6ce181`, 2026-09-02. 규칙과 열 설명은 [README.md](README.md). 항목 수: 23.

## classes/

| 심볼 | 위치 | 유래 | 대체 API | 비고 |
|---|---|---|---|---|
| `Context::_getBrowserTitle()` | `classes/context/Context.class.php:839` | XE | 추정: `self::getBrowserTitle()` |  |
| `Context::normalizeFilePath()` | `classes/context/Context.class.php:2174` | XE | 없음 | 내부 경로 정규화. 절대 경로는 FileHandler::getRealPath(); 코어 호출 있음 |
| `Context::getAbsFileUrl()` | `classes/context/Context.class.php:2196` | XE | `RX_BASEURL . '상대경로'` | 절대 URL은 Rhymix\Framework\URL::fromServerPath() |
| `Context::addJsFile()` | `classes/context/Context.class.php:2268` | XE | `Context::loadFile([$file, 'head'\|'body', $targetie, $index])` | 2·3번 인자는 무시됨; 코어 호출 있음 |
| `Context::unloadJsFile()` | `classes/context/Context.class.php:2301` | XE | `Context::unloadFile($file)` |  |
| `Context::_getUniqueFileList()` | `classes/context/Context.class.php:2336` | XE | 없음 | 내부 함수. 중복 제거는 FrontEndFileHandler가 수행 |
| `Context::addCSSFile()` | `classes/context/Context.class.php:2372` | XE | `Context::loadFile([$file, $media, '', $index])` | 코어 호출 있음 |
| `Context::unloadCSSFile()` | `classes/context/Context.class.php:2389` | XE | `Context::unloadFile($file)` |  |
| `FrontEndFileHandler::isSsl()` | `classes/frontendfile/FrontEndFileHandler.class.php:85` | XE | `RX_SSL 상수` |  |
| `class XEHttpRequest` | `classes/httprequest/XEHttpRequest.class.php:10` | XE | `Rhymix\Framework\HTTP` |  |

## modules/file/

| 심볼 | 위치 | 유래 | 대체 API | 비고 |
|---|---|---|---|---|
| `FileController::printUploadedFileList()` | `modules/file/file.controller.php:2041` | XE | 없음 | no-op; 코어 호출 있음 |

## modules/layout/

| 심볼 | 위치 | 유래 | 대체 API | 비고 |
|---|---|---|---|---|
| `LayoutAdminController::procLayoutAdminInsert()` | `modules/layout/layout.admin.controller.php:21` | XE | 없음 | 일반 레이아웃 인스턴스 생성 액션으로 module.xml에 여전히 등록. faceoff 생성만 거부 |
| `LayoutAdminController::procLayoutAdminUserValueInsert()` | `modules/layout/layout.admin.controller.php:447` | XE | 없음 | FaceOff 레이아웃 기능 폐기 |
| `LayoutAdminController::procLayoutAdminUserLayoutImport()` | `modules/layout/layout.admin.controller.php:568` | XE | 없음 | FaceOff 레이아웃 기능 폐기, FeatureDisabled 예외 |
| `LayoutAdminView::dispLayoutAdminLayoutModify()` | `modules/layout/layout.admin.view.php:348` | XE | 없음 | FaceOff 편집 화면. 레이아웃 코드 편집은 LayoutAdminView::dispLayoutAdminEdit() |
| `LayoutModel::getDefaultLayoutPath()` | `modules/layout/layout.model.php:775` | XE | 없음 | FaceOff 전용 경로; 코어 호출 있음 |
| `LayoutModel::doActivateFaceOff()` | `modules/layout/layout.model.php:844` | XE | 없음 | FaceOff 레이아웃 기능 폐기; 코어 호출 있음 |

## modules/member/

| 심볼 | 위치 | 유래 | 대체 API | 비고 |
|---|---|---|---|---|
| `MemberAdminController::procMemberAdminUpdateJoinForm()` | `modules/member/member.admin.controller.php:1017` | XE | 없음 | module.xml에 여전히 등록된 액션. 가입 폼 순서 변경(up/down)·삭제 처리 |
| `MemberAdminController::moveJoinFormUp()` | `modules/member/member.admin.controller.php:1721` | XE | 없음 | 내부 함수. procMemberAdminUpdateJoinForm(mode=up) 경유; 코어 호출 있음 |
| `MemberAdminController::moveJoinFormDown()` | `modules/member/member.admin.controller.php:1768` | XE | 없음 | 내부 함수. procMemberAdminUpdateJoinForm(mode=down) 경유; 코어 호출 있음 |
| `MemberController::procMemberSaveDocument()` | `modules/member/member.controller.php:510` | XE | `DocumentController::procDocumentTempSave()` | - instead Document Controller - procDocumentTempSave method use |

## modules/module/

| 심볼 | 위치 | 유래 | 대체 API | 비고 |
|---|---|---|---|---|
| `ModuleController::updateModuleSkinVars()` | `modules/module/module.controller.php:740` | XE | `ModuleController::insertModuleSkinVars($module_srl, $obj)` | 현재 no-op |

## modules/point/

| 심볼 | 위치 | 유래 | 대체 API | 비고 |
|---|---|---|---|---|
| `PointAdminController::cacheActList()` | `modules/point/point.admin.controller.php:516` | XE | 없음 | no-op. 포인트 액션 목록 캐시 제거 |

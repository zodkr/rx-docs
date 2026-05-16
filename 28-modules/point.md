# point (포인트)

## 개요

- **카테고리**: member
- **역할**: 회원 포인트 관리. 글/댓글/추천 등 활동에 포인트 지급. 회원 등급(level) 자동 산정.

## 주요 클래스

| 클래스 | 파일 |
|---|---|
| `Point` | `point.class.php` |
| `PointController` | `point.controller.php` |
| `PointModel` | `point.model.php` |
| `PointView` | `point.view.php` |
| `PointAdminController` | `point.admin.controller.php` |
| `PointAdminView` | `point.admin.view.php` |

(`point.admin.model.php`, `point.mobile.php`, `point.api.php`는 없다.)

## 주요 액션 (11개)

| 액션 | 비고 |
|---|---|
| `getMembersPointInfo` | 회원 포인트 정보 모델 (member) |
| `dispPointAdminConfig` | 포인트 설정 (admin_index) |
| `dispPointAdminModuleConfig` | 모듈별 포인트 설정 화면 |
| `dispPointAdminPointList` | 회원 포인트 목록 |
| `procPointAdminInsertConfig` | 설정 저장 (ruleset=insertConfig) |
| `procPointAdminInsertModuleConfig` | 모듈 설정 저장 |
| `procPointAdminUpdatePoint` | 회원 포인트 수정 (ruleset=updatePoint) |
| `procPointAdminInsertPointModuleConfig` | 모듈별 포인트 설정 (manager:config:*) |
| `procPointAdminReCal` | 포인트 재계산 |
| `procPointAdminApplyPoint` | 포인트 일괄 적용 |
| `procPointAdminReset` | 회원 포인트 리셋 |

(레벨 정의는 별도 액션이 없고 `dispPointAdminConfig`에 통합되어 있다.)

## DB 스키마

| 테이블 | 정의 파일 | 용도 |
|---|---|---|
| `point` | `schemas/point.xml` | 회원별 포인트 (`member_srl`, `point`, `regdate`) |

(`point_level_config` 같은 별도 테이블은 없다 — 레벨 정의는 회원 모듈 설정에 직렬화 저장된다.)

## API

```php
$oPointController = getController('point');
$oPointController->setPoint($member_srl, $points, 'add');     // 가산
$oPointController->setPoint($member_srl, $points, 'minus');   // 차감
$oPointController->setPoint($member_srl, $points, 'signed');  // 부호 그대로

$oPointModel = getModel('point');
$current = $oPointModel->getPoint($member_srl);
$level = $oPointModel->getLevel($member_srl);
```

## 이 모듈이 hook하는 트리거

트리거 등록은 `module_trigger` 테이블에 자동 INSERT/DELETE로 동작한다. 정의는 `point.class.php`의 정적 배열 2개:

- `$_insert_triggers` (22개) — 설치 시 추가하고 유지.
- `$_delete_triggers` (3개) — 설치 후 발견되면 제거(예전 버전에서 등록되었던 잔재 정리).

| # | 트리거 (시점) | 메서드 | 비고 |
|---|---|---|---|
| 회원 ||||
| 1 | `member.insertMember` (after) | `triggerInsertMember` (controller) | 가입 보너스 |
| 2 | `member.doLogin` (after) | `triggerAfterLogin` (controller) | 출석/로그인 포인트 |
| 3 | `member.deleteGroup` (after) | `triggerDeleteGroup` (controller) | 그룹 삭제 시 점수 초기화 |
| 문서 ||||
| 4 | `document.insertDocument` (after) | `triggerInsertDocument` (controller) | 글 작성 |
| 5 | `document.updateDocument` (before) | `triggerBeforeUpdateDocument` (controller) | 수정 전 상태 캡처 |
| 6 | `document.updateDocument` (after) | `triggerAfterUpdateDocument` (controller) | 수정 후 점수 정산 |
| 7 | `document.deleteDocument` (after) | `triggerDeleteDocument` (controller) | 글 삭제 시 차감 |
| 8 | `document.moveDocumentToTrash` (after) | `triggerTrashDocument` (controller) | 휴지통 처리 |
| 9 | `document.updateReadedCount` (after) | `triggerUpdateReadedCount` (controller) | 조회 포인트 |
| 10 | `document.updateVotedCount` (after) | `triggerUpdateVotedCount` (controller) | 추천 포인트 |
| 11 | `document.updateVotedCountCancel` (after) | `triggerUpdateVotedCount` (controller) | 추천 취소 |
| 댓글 ||||
| 12 | `comment.insertComment` (after) | `triggerInsertComment` (controller) | 댓글 작성 |
| 13 | `comment.updateComment` (after) | `triggerUpdateComment` (controller) | 댓글 수정 |
| 14 | `comment.deleteComment` (after) | `triggerDeleteComment` (controller) | 댓글 삭제 |
| 15 | `comment.moveCommentToTrash` (after) | `triggerTrashComment` (controller) | 댓글 휴지통 |
| 16 | `comment.updateVotedCount` (after) | `triggerUpdateVotedCount` (controller) | 댓글 추천 |
| 17 | `comment.updateVotedCountCancel` (after) | `triggerUpdateVotedCount` (controller) | 댓글 추천 취소 |
| 파일 ||||
| 18 | `file.deleteFile` (after) | `triggerDeleteFile` (controller) | 파일 삭제 |
| 19 | `file.downloadFile` (before) | `triggerBeforeDownloadFile` (controller) | 다운로드 점수 확인 |
| 20 | `file.downloadFile` (after) | `triggerDownloadFile` (controller) | 다운로드 점수 차감 |
| 모듈 메타 ||||
| 21 | `module.procModuleAdminCopyModule` (after) | `triggerCopyModule` (controller) | 모듈 복사 시 점수 설정 복사 |
| 22 | `module.dispAdditionSetup` (after, view) | `triggerDispPointAdditionSetup` (view) | 관리자 모듈 설정 UI에 포인트 옵션 추가 |

**`$_delete_triggers`로 자동 제거되는 항목 (이전 버전 정리용):**

| 트리거 (시점) | 메서드 | 사유 |
|---|---|---|
| `document.updateDocument` (before) | `triggerUpdateDocument` (controller) | `triggerBeforeUpdateDocument`/`triggerAfterUpdateDocument`로 분리됨 |
| `document.deleteDocument` (before) | `triggerBeforeDeleteDocument` (controller) | 현재 버전은 after만 사용 |
| `file.insertFile` (after) | `triggerInsertFile` (controller) | 더 이상 사용하지 않음 |

각 모듈 설정에서 포인트 조정 가능 (모듈별 `module_config.point_*` 값).

## 이 모듈이 정의하는 트리거

| 이름 | 시점 |
|---|---|
| `point.setPoint` | before/after — `PointController::setPoint($member_srl, $point, $mode)` 내부에서 발사. 외부 모듈이 hook해서 포인트 변화 알림 등 가능 |

## 관련 애드온/위젯

- `addons/point_level_icon/` — 회원 레벨 아이콘 자동 표시.

## 관련

- member: [member.md](member.md)
- 애드온: [../29-addons/point_level_icon.md](../29-addons/point_level_icon.md)

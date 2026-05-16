# communication (커뮤니케이션)

## 개요

- **카테고리**: member
- **역할**: 회원간 쪽지(message)와 친구 관리.

## 주요 클래스

| 클래스 | 파일 |
|---|---|
| `Communication` | `communication.class.php` |
| `CommunicationController` | `communication.controller.php` |
| `CommunicationModel` | `communication.model.php` |
| `CommunicationView` | `communication.view.php` |
| `CommunicationMobile` | `communication.mobile.php` |
| `CommunicationAdminController` | `communication.admin.controller.php` |
| `CommunicationAdminModel` | `communication.admin.model.php` |
| `CommunicationAdminView` | `communication.admin.view.php` |

(`communication.api.php`는 없다.)

## 주요 액션 (22개)

### 쪽지

| 액션 | 비고 |
|---|---|
| `dispCommunicationMessages` | 쪽지함 (member) |
| `dispCommunicationSendMessage` | 쪽지 작성 (route=messages/send) |
| `dispCommunicationNewMessage` | 새 쪽지 알림 (route=messages/new) |
| `dispCommunicationMessageBoxList` | (모바일) 쪽지함 목록 |
| `procCommunicationSendMessage` | 발송 처리 (ruleset=sendMessage) |
| `procCommunicationStoreMessage` / `procCommunicationRestoreMessage` | 보관/복원 |
| `procCommunicationDeleteMessage` / `procCommunicationDeleteMessages` | 단건/일괄 삭제 |
| `procCommunicationUpdateAllowMessage` | 쪽지 수신 허용 토글 |

### 친구

| 액션 | 비고 |
|---|---|
| `dispCommunicationFriend` | 친구 목록 (route=friends) |
| `dispCommunicationAddFriend` / `dispCommunicationAddFriendGroup` | 친구/그룹 추가 폼 |
| `procCommunicationAddFriend` | 친구 추가 (ruleset=addFriend) |
| `procCommunicationAddFriendGroup` | 그룹 추가 (ruleset=addFriendGroup) |
| `procCommunicationMoveFriend` / `procCommunicationDeleteFriend` | 그룹 이동/삭제 |
| `procCommunicationDeleteFriendGroup` / `procCommunicationRenameFriendGroup` | 그룹 삭제/이름변경 |

### 관리자

| 액션 | 비고 |
|---|---|
| `dispCommunicationAdminConfig` | 관리자 설정 (admin_index) |
| `getCommunicationAdminColorset` | 컬러셋 조회 |
| `procCommunicationAdminInsertConfig` | 설정 저장 (ruleset=insertConfig) |

## DB 스키마

| 테이블 | 정의 파일 |
|---|---|
| `member_message` | `schemas/member_message.xml` — 쪽지 |
| `member_friend` | `schemas/member_friend.xml` — 친구 (양방향) |
| `member_friend_group` | `schemas/member_friend_group.xml` — 친구 그룹 |

(테이블 이름이 `communication_*`가 아니라 `member_*` prefix — XE 시대부터의 명명 관습.)

## 이 모듈이 정의하는 트리거

| 이름 | 시점 |
|---|---|
| `communication.sendMessage` | before/after — 쪽지 발송 |
| `communication.deleteMessage` | before/after — 단일 쪽지 삭제 |
| `communication.deleteMessages` | before/after — 일괄 삭제 |
| `communication.addFriend` | before/after — 친구 추가 |
| `communication.deleteFriend` | before/after — 친구 삭제 |

코어가 자동 발사하는 `act:communication.<액션>.before/after`도 별도로 사용 가능.

## 이 모듈이 hook하는 트리거 (`conf/module.xml`의 `<eventHandlers>`)

| 트리거 (시점) | 메서드 | 용도 |
|---|---|---|
| `moduleHandler.init` (before) | `triggerModuleHandlerBefore` (controller) | 요청 초기에 쪽지 알림(`procCommunicationNewMessage`) 카운트 갱신 |
| `member.getMemberMenu` (before) | `triggerMemberMenu` (controller) | 회원 메뉴에 쪽지보내기/친구추가 항목 추가 |

## 관련

- member: [member.md](member.md)
- ncenterlite: [ncenterlite.md](ncenterlite.md)

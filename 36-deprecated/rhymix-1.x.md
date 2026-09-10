<!-- rx-docs tools 브랜치의 deprecated/generate.py 가 생성. 직접 수정 금지. 대체 API는 같은 브랜치의 deprecated/overrides.json 에서 고친다. -->
# Rhymix 1.x(1.9.x)에서 deprecated 처리된 API

검증 기준: Rhymix 2.1.36, 커밋 `1ae6ce181`, 2026-09-02. 규칙과 열 설명은 [README.md](README.md). 항목 수: 6.

## modules/advanced_mailer/

| 심볼 | 위치 | 유래 | 대체 API | 비고 |
|---|---|---|---|---|
| `Advanced_MailerModel::triggerReplaceMailClass()` | `modules/advanced_mailer/advanced_mailer.model.php:12` | 1.x | 없음 | no-op. 메일 드라이버는 Rhymix\Framework\Mail 설정으로 교체; 1.9.0에서 표시 |

## modules/member/

| 심볼 | 위치 | 유래 | 대체 API | 비고 |
|---|---|---|---|---|
| `MemberModel::_getAgreement()` | `modules/member/member.model.php:159` | XE | 없음 | 구버전 약관 파일 읽기. 약관은 회원 설정 agreements 배열; 1.9.0에서 표시; 코어 호출 있음 |

## modules/point/

| 심볼 | 위치 | 유래 | 대체 API | 비고 |
|---|---|---|---|---|
| `PointModel::getMembersPointInfo()` | `modules/point/point.model.php:154` | XE | `PointModel::getPoint($member_srl)` | 요청 변수 member_srls를 읽는 액션형 메서드; 1.9.0에서 표시 |

## modules/poll/

| 심볼 | 위치 | 유래 | 대체 API | 비고 |
|---|---|---|---|---|
| `PollModel::getPollHtml()` | `modules/poll/poll.model.php:212` | XE | 없음 | this function uses poll skin, which will be removed; poll 스킨과 함께 제거 예정. 설문 표시는 poll 모듈 템플릿; 1.9.0에서 표시 |
| `PollModel::getPollResultHtml()` | `modules/poll/poll.model.php:272` | XE | 없음 | this function uses poll skin, which will be removed; poll 스킨과 함께 제거 예정. 설문 표시는 poll 모듈 템플릿; 1.9.0에서 표시; 코어 호출 있음 |
| `PollModel::getPollGetColorsetList()` | `modules/poll/poll.model.php:320` | XE | 없음 | this function uses poll skin, which will be removed; poll 스킨과 함께 제거 예정. 설문 표시는 poll 모듈 템플릿; 1.9.0에서 표시 |

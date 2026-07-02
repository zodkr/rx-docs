# importer (데이터 이전)

## 개요

- **카테고리**: migration
- **역할**: XML 파일을 이용해 회원/게시판 데이터를 대량 입력. 외부 시스템에서 마이그레이션할 때 사용.

## 주요 클래스

| 클래스 | 파일 |
|---|---|
| `Importer` | `importer.class.php` |
| `ImporterAdminController` | `importer.admin.controller.php` |
| `ImporterAdminView` | `importer.admin.view.php` |
| `Extract` | `extract.class.php` (XE legacy export/import 유틸) |
| `Ttimport` | `ttimport.class.php` (TextCube 가져오기 전용) |

(importer는 일반 controller/model/view를 두지 않는다 — 관리자 전용 모듈.)

## 주요 액션 (5개)

| 액션 | 비고 |
|---|---|
| `dispImporterAdminImportForm` | 이전 폼 (admin_index, menu=importer) |
| `procImporterAdminImport` | 이전 실행 |
| `procImporterAdminPreProcessing` | 사전 추출·캐싱 (XML을 항목별 캐시 파일로 분리하고 index 생성) |
| `procImporterAdminSync` | 동기화 |
| `procImporterAdminCheckXmlFile` | XML 파일 검증 |

## XML 포맷

XE 호환 export XML 형식. 타입에 따라 최상위 노드가 다르다.

| 타입 | 최상위 / 항목 노드 | 위치 |
|---|---|---|
| 회원 | `<members>` / `<member>` | `importer.admin.controller.php:160` |
| 쪽지 | `<messages>` / `<message>` | `importer.admin.controller.php:164` |
| 모듈 게시글 | `<posts>` / `<post>` | `importer.admin.controller.php:232` |

`<post>` 내부에는 `<comments>`, `<trackbacks>`, `<attaches>`, `<extra_vars>` 노드가 중첩된다. `title`·`content` 등 각 필드 값은 base64로 인코딩되어 있으며 임포트 시 `base64_decode`로 복원한다 (`importer.admin.controller.php:738`). 게시글 XML에는 `<module_srl>`이 없고, 대상 모듈은 임포트 화면에서 지정한 `target_module`로 결정된다 (`importer.admin.controller.php:265`, `:684`).

```xml
<?xml version="1.0" encoding="UTF-8"?>
<posts module="...">
    <post>
        <title><!-- base64 --></title>
        <content><!-- base64 --></content>
        <regdate>...</regdate>
        <comments>
            <comment>...</comment>
        </comments>
        <attaches>
            <attach>...</attach>
        </attaches>
        <extra_vars>...</extra_vars>
    </post>
</posts>
```

## 동작

- 대용량 처리를 위해 청크 단위로 처리.
- 진행률 표시.
- 트랜잭션/롤백은 지원하지 않는다. 청크 단위로 즉시 커밋되고 처리 완료된 임시 캐시 파일은 삭제되므로 (`importer.admin.controller.php:346`, `:838`) 중단 시 이미 입력된 데이터는 남는다.

## 관련

- module: [module.md](module.md)
- CLI 스크립트: [../21-cli-and-scripts.md](../21-cli-and-scripts.md)

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
| `procImporterAdminPreProcessing` | 사전 처리 (파일 검사 등) |
| `procImporterAdminSync` | 동기화 |
| `procImporterAdminCheckXmlFile` | XML 파일 검증 |

## XML 포맷

XE 호환 export XML 형식. document/comment/file/member 노드를 포함.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<documents>
    <document>
        <module_srl>1</module_srl>
        <title>제목</title>
        <content>본문</content>
        ...
    </document>
</documents>
```

## 동작

- 대용량 처리를 위해 청크 단위로 처리.
- 진행률 표시.
- 실패 시 롤백 가능.

## 관련

- module: [module.md](module.md)
- CLI 스크립트: [../21-cli-and-scripts.md](../21-cli-and-scripts.md)

# 14. 데이터베이스와 쿼리

Rhymix의 DB 추상화는 두 부분으로 구성된다.

- **`Rhymix\Framework\DB`** (`common/framework/DB.php`) — PDO MySQL 기반 저수준 API.
- **선언적 XML 쿼리** — `modules/<n>/queries/*.xml`을 `executeQuery()`로 호출.

## DB 인스턴스

```php
$db = Rhymix\Framework\DB::getInstance();         // 기본 master
$db = Rhymix\Framework\DB::getInstance('slave');  // 다중 DB 분리 시
```

설정은 `db.master.*` / `db.<type>.*` (`files/config/config.php`).

```php
'db' => [
    'master' => [
        'type' => 'mysql',
        'host' => 'localhost',
        'port' => 3306,
        'user' => 'rhymix',
        'pass' => '...',
        'database' => 'rhymix',
        'prefix' => 'rx_',
        'charset' => 'utf8mb4',
        'engine' => 'innodb',
    ],
]
```

## 저수준 API

`DB::getInstance()->...` 인스턴스 메서드.

| 메서드 | 비고 |
|---|---|
| `prepare($sql, $opts=[])` | PDO 준비 (`DBStmtHelper` 반환) |
| `query($sql, ...$args)` | 즉시 실행 |
| `executeQuery($query_id, $args=[], $col=[], $result_type='auto', $result_class='')` | XML 쿼리 실행. `$result_type='array'`로 강제 가능 |
| `fetch($stmt, $last_index=0, $result_type='auto', $result_class='')` | row fetch |
| `getAffectedRows()` | 마지막 쿼리의 영향 행 |
| `getInsertID()` | 마지막 INSERT의 auto increment |
| `getNextSequence()` | 시퀀스 발급 (`rx_sequence` 테이블) |
| `beginTransaction()` / `commit()` / `rollback()` | 트랜잭션 (중첩 카운팅) |
| `createTable($filename='', $content='')` / `dropTable($name)` | 스키마 |
| `addColumn`, `modifyColumn`, `dropColumn` | ALTER |
| `addIndex($table, $name, $columns, $type='', $options='')` / `dropIndex` | 인덱스 |
| `addPrefixes($sql)` | `rx_table` 형태로 prefix 적용 |
| `addQuotes($str)` | 안전 이스케이프 (legacy — prepared statement 권장) |

`executeQueryArray(...)`는 인스턴스 메서드가 아니라 `common/legacy.php`의 글로벌 함수다 — 내부에서 `DB->executeQuery(..., 'array')`를 호출한다.

### 트랜잭션 중첩

```php
$db = DB::getInstance();
$db->beginTransaction();  // 레벨 1
try {
    $db->beginTransaction();  // 레벨 2 (savepoint)
    // ...
    $db->commit();             // 레벨 1로
    // ...
    $db->commit();             // 진짜 commit
} catch (Throwable $e) {
    $db->rollback();           // 가장 바깥까지 롤백
    throw $e;
}
```

## XML 쿼리 시스템

### 호출

```php
$args = (object)['module_srl' => 123, 'category_srl' => 5];
$output = executeQuery('board.getBoardList', $args);
if (!$output->toBool()) {
    // 에러 처리
}
$data = $output->data;          // single row (stdClass) 또는 array
```

```php
$list = executeQueryArray('board.getBoardList', $args)->data ?? [];
```

### Query ID 포맷

`DB::executeQuery()` (`common/framework/DB.php:299-304`)는 `query_id`를 `.`로 split한 뒤:

- 2조각이면 앞에 `'modules'`를 자동 prepend → `board.getList` → `modules/board/queries/getList.xml`
- 3조각이면 그대로 → `widgets.content.getMids` → `widgets/content/queries/getMids.xml`, `addons.<name>.<query>` 등 비-모듈 플러그인도 같은 식으로 호출 가능

파일이 없으면 `setError(-1, "Query '...' does not exist.")` 반환.

### 쿼리 XML 구조

`common/framework/parsers/DBQueryParser.php`가 파싱한다.

```xml
<query id="getBoardList" action="select">
    <tables>
        <table name="documents" alias="d" />
        <table name="modules" alias="m" type="left join">
            <conditions>
                <condition operation="equal" column="m.module_srl" var="d.module_srl" />
            </conditions>
        </table>
    </tables>

    <columns>
        <column name="d.document_srl" />
        <column name="d.title" alias="document_title" />
        <column name="m.mid" />
    </columns>

    <conditions>
        <condition operation="equal" column="d.module_srl" var="module_srl" notnull="notnull" />
        <condition operation="in" column="d.status" default="1,2" var="status" />
        <group pipe="and">
            <condition operation="like_prefix" column="d.title" var="search_title" />
            <condition operation="equal" column="d.user_id" var="user_id" pipe="or" />
        </group>
    </conditions>

    <groups>
        <group column="d.category_srl" />
    </groups>

    <navigation>
        <index var="sort_index" default="d.list_order" order="order_type" />
        <list_count var="list_count" default="20" />
        <page_count var="page_count" default="10" />
        <page var="page" default="1" />
    </navigation>
</query>
```

### `<conditions>` operation 종류

`common/framework/parsers/dbquery/VariableBase.php:115-`의 switch에 정의된 전수 표.

| operation (별칭) | SQL |
|---|---|
| `equal` | `=` |
| `notequal` / `not_equal` | `!=` |
| `more` / `gte` | `>=` |
| `excess` / `gt` | `>` |
| `less` / `lte` | `<=` |
| `below` / `lt` | `<` |
| `regexp` | `REGEXP` |
| `notregexp` / `not_regexp` | `NOT REGEXP` |
| `like` | `LIKE '%val%'` |
| `like_prefix` / `like_head` | `LIKE 'val%'` |
| `like_suffix` / `like_tail` | `LIKE '%val'` |
| `notlike` | `NOT LIKE '%val%'` |
| `notlike_prefix` / `notlike_head` | `NOT LIKE 'val%'` |
| `notlike_suffix` / `notlike_tail` | `NOT LIKE '%val'` |
| `and` / `or` / `xor` | 비트 연산자 (`&` / `\|` / `^`) |
| `null` | `IS NULL` |
| `notnull` / `not_null` | `IS NOT NULL` |
| `in` | `IN (...)` (`,`로 split한 후 각 원소를 bound parameter로) |
| `notin` / `not_in` | `NOT IN (...)` |
| `between` | `BETWEEN ? AND ?` |
| `notbetween` / `not_between` | `NOT BETWEEN ? AND ?` |
| `search` | 공백/따옴표/마이너스 prefix를 해석하는 키워드 검색식으로 변환 (`_parseSearchKeywords`) |
| `plus` / `minus` / `multiply` | **`<column>`(INSERT/UPDATE) 전용**. `col = col ± ?` / `col = col * ?` 형태로 expand |

> `<column>`(ColumnWrite — INSERT/UPDATE 본문)에서는 `equal` / `plus` / `minus` / `multiply` **4개만** 허용. 다른 operation은 `\Rhymix\Framework\Exceptions\QueryError: Operation … is not valid for column in an INSERT or UPDATE query`를 던진다 (`VariableBase.php:110-113`).

> 위 표에 없는 operation(예: 존재하지 않는 `not`)은 switch의 default 분기(`VariableBase.php:271-273`)로 떨어져 `col = ?`(등호 비교)를 조용히 생성한다. 비트 NOT(`~`)을 만드는 코드는 파서 어디에도 없다.

### 조건이 SQL에 포함될지 결정되는 흐름

`var` / `default` / `ifvar` / `notnull` 조합에 따라 condition / group / table / column이 **포함되거나, 건너뛰어지거나, 예외를 던진다**. `VariableBase::getQueryStringAndParams` (`VariableBase.php:24-97`):

1. `if="varname"` (`ifvar`)이 있고 `$args[varname]`이 비어있으면(empty) → **블록 전체를 SQL에서 생략**한다 (condition/group/table/column 모두).
2. `$args[var]` 값이 `Rhymix\Framework\Parsers\DBQuery\NullValue`/`EmptyString` 인스턴스면 명시적 `NULL` / `''` 처리. 특히 `NullValue` + `equal`/`notequal` operation은 자동으로 `null` / `notnull` operation으로 치환.
3. 일반 값이면 그대로 bound parameter로 전달.
4. `$args[var]`이 `''`이고 SELECT/DELETE 쪽이면 `default` 값을 사용. (`<column>`에서는 빈 문자열을 그대로 사용 — INSERT의 빈 컬럼 보존.)
5. `var` 매칭 실패 + `default` 없음 + `notnull="notnull"`이면 **`QueryError` 던짐** ("Variable … is not set").
6. 그 외 (var/default 둘 다 없고 not_null도 아님) — operation이 `null`/`notnull`이 아니면 그냥 **생략**.
7. `var="d.module_srl"`처럼 `\w+\.\w+` 형식이고 `default`가 없으면 var 값 자체를 column-reference default로 잡는다 (`DBQueryParser.php:267-274`) — JOIN ON절 조건에 자주 쓰이는 패턴.

### 태그별 XML 속성

`DBQueryParser`가 각 태그에서 실제로 읽는 속성만 정리. (목록에 없는 속성은 무시된다 — 모든 태그가 같은 속성을 받는 게 아니다.)

#### `<table name="…" alias="…" type="…" if="…" query="true">` (`DBQueryParser.php:57-84`)

| 속성 | 의미 |
|---|---|
| `name` | 테이블명 (prefix 자동 부착) |
| `alias` | 별칭 |
| `type` | `join` 문자열이 포함되면 JOIN으로 처리 (`left join`/`inner join`/`right join`/`cross join` 등). 없으면 단순 FROM에 추가 |
| `if` | `$args[if]`가 비어있으면 테이블 전체 SQL에서 생략 (`ifvar`) |
| `query="true"` | child `<tables>`/`<columns>`/… 를 가진 derived-table 서브쿼리로 파싱 |

JOIN조건은 `<table>` 내부의 `<conditions>` 블록에 적는다.

#### `<column>` — SELECT 컬럼 (`DBQueryParser.php:131-145`, `ColumnRead`)

| 속성 | 의미 |
|---|---|
| `name` | 컬럼식 (`d.title`, `COUNT(*)`, `IF(...)` 등 — `isValidColumnName` 실패하면 `is_expression=true`로 표현식 처리) |
| `alias` | AS 별칭 |
| `if` | 비어있으면 컬럼 생략 |

(SELECT `<column>`은 `var`/`default`/`notnull`/`filter`/`minlength`/`maxlength`/`pipe`를 받지 **않는다** — 그쪽 속성들은 INSERT/UPDATE 쪽 `<column>`이나 `<condition>`에서만 의미가 있다.)

`<columns distinct="distinct">…</columns>`로 SELECT DISTINCT 활성화.

#### `<column>` — INSERT/UPDATE 컬럼 (`DBQueryParser.php:149-160`, `ColumnWrite`)

| 속성 | 의미 |
|---|---|
| `name` | 컬럼명 |
| `operation` | `equal`(기본)/`plus`/`minus`/`multiply` 중 하나. 다른 값은 `QueryError` |
| `var` | `$args[var]`에서 값을 가져옴 |
| `default` | var가 없거나 빈 값일 때 사용. 아래의 default 토큰표 참고 |
| `notnull` | var/default 모두 없으면 `QueryError` |
| `if` | 비어있으면 컬럼 자체를 SQL에서 생략 |
| `filter` | 값 검증 — `email`/`email_address`/`homepage`/`url`/`userid`/`user_id`/`number`/`numbers`/`alpha`/`alnum`/`alpha_number` 중 하나. 실패 시 `QueryError` (`VariableBase.php:405-463`) |
| `minlength` / `maxlength` | 길이 검사 |

(`pipe`는 INSERT/UPDATE `<column>`에서는 의미 없음.)

#### `<condition>` (`DBQueryParser.php:262-282`, `Condition`)

| 속성 | 의미 |
|---|---|
| `operation` | 위의 operation 표 참고 |
| `column` | 조건 좌변 컬럼 |
| `var` | `$args[var]`로 값을 가져옴. `var="t.col"`처럼 `\w+\.\w+` 형식이면서 `default`가 없으면 var 값을 column-default로 해석 (JOIN 조건 패턴) |
| `default` | var가 비었을 때의 기본값 |
| `notnull` | var/default 모두 없으면 `QueryError` |
| `if` | 비어있으면 조건 생략 |
| `filter` | (위 ColumnWrite와 동일 목록) |
| `minlength` / `maxlength` | 길이 검사 |
| `pipe` | `AND`(기본)/`OR` — 이 조건을 앞 조건과 결합하는 boolean operator |

#### `<group>` — 조건 그룹 (`DBQueryParser.php:284-291`, `ConditionGroup`)

| 속성 | 의미 |
|---|---|
| `pipe` | `AND`(기본)/`OR` — 그룹 전체를 결합하는 operator |
| `if` | 비어있으면 그룹 전체 생략 |
| `notnull` | 그룹 단위 not_null 플래그 |

#### `default=` 토큰 (`VariableBase::getDefaultValue` — `VariableBase.php:329-393`)

`default` 속성에 그대로 넣을 수 있는 특수 토큰. 평가 시점은 쿼리 실행 시점.

| 토큰 | 결과 |
|---|---|
| `ipaddress()` | `RX_CLIENT_IP` (현재 요청 IP) |
| `unixtime()` | `time()` (Unix epoch 정수) |
| `timestamp()` / `now()` | `date('Y-m-d H:i:s')` |
| `curdate()` / `datetime()` | `date('YmdHis')` — XE 표준 14자리 datetime |
| `date()` | `date('Ymd')` |
| `time()` | `date('His')` |
| `member_srl()` | 현재 로그인 회원의 `member_srl` (비로그인 시 0) |
| `sequence()` | `getNextSequence()` (글로벌 srl 발급) |
| `null` | 리터럴 `NULL` 삽입 |
| `plus(N)` | `<column> = <column> + N` — 컬럼 증가 |
| `minus(N)` | `<column> = <column> - N` — 컬럼 감소 |
| `multiply(N)` | `<column> = <column> * N` |
| `timestamp(<포맷>)` | `date(<포맷>)` — 임의 포맷 문자열 (예: `timestamp(Y-m)`) |

추가 규칙 (토큰 매칭 전/후의 특례):

1. **`_srl`로 끝나는 컬럼 + 함수형 아님 + 숫자 아님** → `default` 문자열을 컬럼명으로 해석하여 quote. JOIN/co-reference 패턴 보조.
2. **대문자 + `(args)` 패턴** (예: `IF(a,b,c)`, `UNIX_TIMESTAMP(regdate)`, `CONCAT(a,b)`) → 토큰 표에 없어도 SQL 표현식으로 그대로 inject. 판정 정규식이 `/^[A-Z_]+\([^)]+\)/`이라 괄호 안에 최소 1글자를 요구하므로, 괄호가 비어 있는 `NOW()`·`UNIX_TIMESTAMP()`는 매칭되지 않아 SQL 표현식이 아니라 리터럴 바인딩 값으로 처리된다 (현재 시각은 소문자 토큰 `now()`를 사용) (`VariableBase.php:386`).
3. **그 외 문자열/숫자** → 리터럴 값으로 bound parameter.

(`<group>`은 자체 `var`/`default`/`filter`/`minlength`/`maxlength`를 받지 **않는다** — 내부에 들어가는 `<condition>`들이 갖는다.)

### `<navigation>` 자동 페이지네이션

`<navigation>` 절이 있으면 결과에 자동으로 `page_navigation` 객체가 포함된다.

```php
$output = executeQuery('board.getBoardList', $args);
$documents = $output->data;
$page_navigation = $output->page_navigation;     // PageHandler 인스턴스
$total_count = $output->total_count;
$total_page = $output->total_page;
```

`<navigation>`의 child 태그 (`Navigation.php` + `DBQueryParser.php:191-215`):

| 태그 | 속성 | 의미 |
|---|---|---|
| `<index>` | `var` / `default` / `order` / `orderdefault="asc\|desc"` / `if` | ORDER BY 컬럼. `var`로 정렬 컬럼을 받고(`default`로 fallback), `order`로 정렬 방향 변수명(`asc`/`desc`)을 받는다. `orderdefault`는 방향 기본값(default `ASC`). 여러 번 선언 가능. |
| `<list_count>` | `var` / `default` | 페이지당 행 수 |
| `<page_count>` | `var` / `default` | 페이지 그룹 크기 (이전/다음 버튼용) |
| `<page>` | `var` / `default` | 현재 페이지 번호 |
| `<offset>` | `var` / `default` | OFFSET (페이지네이션 대신 단순 OFFSET 모드) |

### action 종류

`<query action="…">`. 파서는 `strtoupper($attribs['action'])`로 정규화 후 4개 case만 매칭한다 (`Query.php:72-88`). 그 외 값은 빈 SQL을 반환하므로 사실상 무효.

- `select` (또는 미지정 — 기본값) — SELECT.
- `insert` — INSERT. `updateduplicate="true"`를 함께 주면 `ON DUPLICATE KEY UPDATE`(upsert)로 처리 (`DBQueryParser.php:237-243`).
- `update` — UPDATE.
- `delete` — DELETE.

(과거 XE 호환 문서에 보이는 `select-list` / `insert-select`는 **현재 Rhymix 파서가 지원하지 않는다** — `SELECT-LIST` 같은 정규화 결과가 switch의 어떤 case에도 매칭되지 않아 빈 문자열을 반환한다. 코어 모듈 어디에서도 사용되지 않음.)

### 기타 쿼리 옵션

- **SELECT DISTINCT**: `<columns distinct="distinct">…</columns>` (`DBQueryParser.php:227-234`).
- **INSERT … ON DUPLICATE KEY UPDATE**: `<query action="insert" updateduplicate="true">`.
- **인덱스 힌트**: `<index_hint for="MYSQL|ALL"><(이름 자유) name="idx_x" type="use|force|ignore" table="d" /></index_hint>` — `for`가 `ALL`이거나 현재 DB 드라이버와 일치할 때만 적용 (`DBQueryParser.php:86-121`).
- **`<groups>` + `<having>`**: `<groups><group column="d.member_srl" /><having><condition operation="more" column="cnt" var="min_count" /></having></groups>` — HAVING 절 (`DBQueryParser.php:183-186`).
- **서브쿼리(테이블 자리)**: `<tables><table query="true" alias="A"><tables>…</tables>…</table></tables>` — FROM 절 또는 JOIN 절의 derived table로 사용 (`DBQueryParser.php:57-64`).
- **서브쿼리(컬럼 자리)**: `<columns>` 안에 `<query id="…" action="select">…</query>`를 두면 SELECT 컬럼으로 들어간다 (`DBQueryParser.php:126-130`).

### subquery / join 고급

`<conditions>` 안의 `<query>`는 IN-subquery 등에 사용한다 (`DBQueryParser.php:293-298`).

```xml
<conditions>
    <condition operation="in" column="d.member_srl" pipe="and">
        <query action="select">
            <tables>
                <table name="member_group_member" alias="g" />
            </tables>
            <columns>
                <column name="g.member_srl" />
            </columns>
            <conditions>
                <condition operation="equal" column="g.group_srl" var="group_srl" />
            </conditions>
        </query>
    </condition>
</conditions>
```

## 스키마 XML (`schemas/*.xml`)

`modules/<n>/schemas/<table>.xml`. 모듈 설치 시 자동 생성된다. `DBTableParser`가 파싱.

```xml
<table name="board_categories">
    <column name="category_srl" type="number" size="11" notnull="notnull" primary_key="primary_key" />
    <column name="module_srl"   type="number" size="11" notnull="notnull" />
    <column name="title"        type="varchar" size="100" notnull="notnull" />
    <column name="list_order"   type="number" size="11" default="0" notnull="notnull" />
    <column name="regdate"      type="date" notnull="notnull" />
    <index name="idx_module_srl" columns="module_srl" />
    <index name="unique_module_title" columns="module_srl,title" type="unique" />
</table>
```

### XE 호환 타입 매핑

| XE 타입 | MySQL 타입 |
|---|---|
| `number` | `bigint` (size와 무관하게 항상 `bigint`, size는 무시) |
| `bignumber` | `bigint` |
| `varchar` | `varchar(size)` |
| `text` | `text` |
| `bigtext` | `longtext` |
| `date` | `char(14)` (YYYYMMDDHHMMSS 형식) |
| `char` | `char(size)` |
| `float` | `float` |
| `double` | `double` |

`date`가 char로 매핑되는 이유는 XE가 자체 `YYYYMMDDHHMMSS` 형식을 사용하기 때문. `ztime()` 헬퍼로 변환.

## 시퀀스 (sequence)

```php
$seq = getNextSequence();       // rx_sequence 테이블에서 발급
```

- 글로벌 단일 시퀀스. `document_srl`, `comment_srl`, `file_srl` 등 모두 공유.
- 충돌 없이 모든 콘텐츠 srl을 발급할 수 있어 외부 시스템 연동에 유리.

## 쿼리 디버깅

### 쿼리 로그

`config('debug.display_content')`에 `queries` 또는 `slow_queries` 포함 시 모든 쿼리/슬로우 쿼리가 디버그 출력에 포함.

### 쿼리 주석

`config('debug.query_comment') = true`면 실행되는 모든 SQL의 끝에 `/* <query_id> <클라이언트 IP> */` 형태의 주석이 자동 부착된다 (예: `/* board.getBoardList 1.2.3.4 */`). 직접 `prepare()` / `query()` / `_query()`로 실행하는 경우에는 query_id 대신 각각 `prepare()` / `query()` / `_query()` 라벨이 들어간다 (`DB.php:384`, `DB.php:236`, `DB.php:198`, `DB.php:1425`).

### 전체 스택

`config('debug.query_full_stack') = true`면 호출 스택 전체가 주석으로 들어간다.

### 쿼리 로그 조회

```php
$log = Rhymix\Framework\Debug::getQueries();      // 전체 쿼리
$slow = Rhymix\Framework\Debug::getSlowQueries(); // 슬로우 쿼리
// 각 원소는 stdClass:
// { query_id, query_string, query_time, query_connection, message, error_code, file, line, method, backtrace, count, time, type }
```

`Debug::getQueryLog()`는 존재하지 않는다. `DB::getQueryLog($query, $elapsed_time)`는 로그 항목 하나를 만드는 DB 인스턴스 내부용 빌더다 (`DB.php:1289`).

## 헬퍼

### DBResultHelper

`executeQuery` 결과 객체. 다음 속성 접근:

- `data` — 결과 행 (single row 또는 array, query action에 따름).
- `page_navigation` — 페이지네이션 객체.
- `total_count`, `total_page`, `page`.
- `add()`로 추가 변수 부착 가능.

### DBStmtHelper

`prepare()` 결과. `execute($params)`, `fetch()`, `fetchAll()` 가능.

## 흔한 패턴

### CRUD

```php
// 조회
$output = executeQuery('board.getDocument', (object)['document_srl' => $srl]);
$doc = $output->data;

// 등록
$args = (object)[
    'document_srl' => getNextSequence(),
    'module_srl' => $module_srl,
    'title' => '제목',
    'content' => '<p>본문</p>',
    'regdate' => date('YmdHis'),
];
$output = executeQuery('document.insertDocument', $args);

// 트랜잭션
$db = DB::getInstance();
$db->beginTransaction();
try {
    executeQuery('document.insertDocument', $args);
    executeQuery('document.updateModuleCount', $args2);
    $db->commit();
} catch (Throwable $e) {
    $db->rollback();
    throw $e;
}
```

### 동적 컬럼 제한

```php
$output = executeQuery('document.getDocumentList', $args, ['document_srl', 'title']);
// SELECT 절을 두 컬럼만으로 제한
```

## 다음 문서

- 설정: [25-config-system.md](25-config-system.md)
- 디버그: [24-debug-and-logging.md](24-debug-and-logging.md)

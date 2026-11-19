# Drift 모니터링 DB 설계서

작성일: 2026-06-17

## 1. 목적

이 문서는 현재 Markdown/CSV 기반으로 관리되는 drift method, algorithm variant, measurement, parameter, chart, 문서 해석 정보를 RDB로 이전하기 위한 논리 설계를 정의한다.

목표는 단순히 문서 원문을 DB에 넣는 것이 아니라, 다음 항목을 운영 가능한 단위로 분해해 관리하는 것이다.

```text
method
  -> algorithm variant
  -> measurement / parameter / chart
  -> algorithm implementation
  -> execution run / result
  -> chart rendering
  -> document section / interpretation knowledge
```

## 2. 설계 원칙

1. Markdown과 CSV는 초기 import source로 본다.
2. RDB는 운영 앱, 알고리즘 실행기, 차트 렌더러가 읽는 기준 catalog/index/store 역할을 한다.
3. 사람이 읽는 설명 문장은 section 단위로 저장하되, chart id, method id, variant id, measurement id는 FK로 구조화한다.
4. 모든 import row는 원천 추적성을 가진다.
5. ID는 surrogate key와 stable natural key를 함께 둔다.
6. 실제 알고리즘 실행 결과와 차트 렌더링 결과는 catalog table과 분리한다.
7. 자유도가 큰 설정은 JSON 컬럼을 허용하되, 검색/조인해야 하는 값은 정규 컬럼으로 승격한다.

권장 DB는 PostgreSQL이다. SQLite로 시작할 수 있지만, 운영 단계에서는 JSONB, full-text search, partial index, transaction 처리 측면에서 PostgreSQL이 적합하다.

## 3. 전체 테이블 그룹

| 그룹 | 테이블 | 역할 |
|---|---|---|
| Source 관리 | `source_document`, `source_import_batch` | Markdown/CSV 원천과 import 이력 |
| Method catalog | `drift_method`, `algorithm_variant`, `method_variant` | drift method와 variant 기준 정보 |
| Measurement/Parameter | `measurement`, `parameter`, `variant_measurement`, `variant_parameter` | 산출값과 설정값 |
| Chart catalog | `chart_definition`, `chart_asset`, `variant_chart` | chart id, chart 코드/이미지, variant-chart 연결 |
| Chart component catalog | `chart_component`, `chart_component_usage`, `chart_component_raw_mapping`, `chart_component_interpretation_rule` | chart component 의미, chart별 사용 component, 원본 component 표현, 그래프 관점 해석 규칙 |
| Chart interpretation guide | `chart_interpretation_guide` | component별 그래프 판독을 chart 전체 관점으로 종합하는 해석 가이드 |
| 문서 지식 | `document_section`, `section_entity_link` | 문서 분해 section과 entity 연결 |
| 구현/실행 | `algorithm_implementation`, `algorithm_run`, `algorithm_result` | 실제 알고리즘 구현과 실행 결과 |
| 차트 렌더링 | `chart_render_job`, `chart_render_output` | 실행 결과 기반 차트 생성 |
| 운영 보조 | `tag`, `entity_tag`, `audit_log` | 검색/분류/변경 추적 |

## 4. Source 관리

### 4.1 `source_document`

Markdown, CSV, JS 생성 파일 등 import 원천을 기록한다.

| 컬럼 | 타입 | Key | 설명 |
|---|---|---|---|
| `source_document_id` | bigint | PK | 내부 ID |
| `source_path` | text | UK | 저장소 기준 상대 경로 |
| `source_type` | varchar(30) | IDX | `markdown`, `csv`, `generated_js`, `html`, `image` |
| `domain` | varchar(50) | IDX | `method`, `variant`, `chart`, `measurement`, `parameter`, `document` |
| `title` | text |  | 문서 제목 |
| `checksum_sha256` | char(64) | IDX | 파일 내용 해시 |
| `file_size_bytes` | bigint |  | 파일 크기 |
| `last_seen_at` | timestamptz |  | 마지막 import 확인 시각 |
| `is_active` | boolean | IDX | 현재 유효 원천 여부 |

제약:

```sql
unique(source_path)
check(source_type in ('markdown','csv','generated_js','html','image','code','other'))
```

### 4.2 `source_import_batch`

한 번의 import 작업을 기록한다.

| 컬럼 | 타입 | Key | 설명 |
|---|---|---|---|
| `import_batch_id` | bigint | PK | import batch ID |
| `started_at` | timestamptz | IDX | 시작 시각 |
| `finished_at` | timestamptz |  | 종료 시각 |
| `import_status` | varchar(20) | IDX | `running`, `success`, `failed` |
| `git_commit_sha` | char(40) | IDX | import 대상 Git commit |
| `source_root` | text |  | import 기준 루트 |
| `summary_json` | jsonb |  | import 개수/오류 요약 |
| `error_message` | text |  | 실패 메시지 |

## 5. Method Catalog

### 5.1 `drift_method`

drift monitoring method 자체를 관리한다.

| 컬럼 | 타입 | Key | 설명 |
|---|---|---|---|
| `drift_method_id` | bigint | PK | 내부 ID |
| `method_code` | varchar(80) | UK | 안정 코드. 예: `KS_TEST`, `WASSERSTEIN_DISTANCE` |
| `display_name` | text | UK | 표시명. 예: `KS Test` |
| `method_category` | varchar(80) | IDX | `BatchDistributionComparison` 등 |
| `primary_input_type` | varchar(80) | IDX | `numeric_sample`, `category_count`, `stream`, `embedding` 등 |
| `primary_output_type` | varchar(80) |  | `p_value`, `distance`, `alarm`, `ranking` 등 |
| `status` | varchar(20) | IDX | `draft`, `active`, `deprecated` |
| `summary` | text |  | method 요약 |
| `created_at` | timestamptz |  | 생성 시각 |
| `updated_at` | timestamptz |  | 수정 시각 |

제약:

```sql
unique(method_code)
unique(display_name)
check(status in ('draft','active','deprecated'))
```

### 5.2 `algorithm_variant`

variant 자체의 안정 식별자와 설명을 관리한다.

| 컬럼 | 타입 | Key | 설명 |
|---|---|---|---|
| `algorithm_variant_id` | bigint | PK | 내부 ID |
| `variant_code` | varchar(120) | UK | 예: `TWO_SAMPLE_KS_TWO_SIDED` |
| `display_name` | text |  | 표시명 |
| `variant_family` | varchar(120) | IDX | `KS_TEST`, `ADWIN`, `MMD` 등 |
| `status` | varchar(20) | IDX | `draft`, `active`, `deprecated` |
| `use_when_text` | text |  | 사용 조건 |
| `good_for_text` | text |  | 적합 대상 |
| `avoid_when_text` | text |  | 회피 조건 |
| `caution_text` | text |  | 주의사항 |
| `report_guidance_text` | text |  | 보고서 문장 가이드 |
| `source_document_id` | bigint | FK | 원천 variant 문서 |
| `created_at` | timestamptz |  | 생성 시각 |
| `updated_at` | timestamptz |  | 수정 시각 |

제약:

```sql
unique(variant_code)
foreign key(source_document_id) references source_document(source_document_id)
```

### 5.3 `method_variant`

method와 variant의 연결을 관리한다.

| 컬럼 | 타입 | Key | 설명 |
|---|---|---|---|
| `method_variant_id` | bigint | PK | 내부 ID |
| `drift_method_id` | bigint | FK, IDX | method |
| `algorithm_variant_id` | bigint | FK, IDX | variant |
| `is_default_variant` | boolean | IDX | method의 기본 추천 variant 여부 |
| `selection_priority` | integer | IDX | 추천 우선순위 |
| `selection_rule_text` | text |  | 선택 규칙 |
| `source_document_id` | bigint | FK | 원천 문서 |

제약:

```sql
unique(drift_method_id, algorithm_variant_id)
foreign key(drift_method_id) references drift_method(drift_method_id)
foreign key(algorithm_variant_id) references algorithm_variant(algorithm_variant_id)
```

## 6. Measurement/Parameter

### 6.1 `measurement`

표준 측정값 catalog다.

| 컬럼 | 타입 | Key | 설명 |
|---|---|---|---|
| `measurement_id` | bigint | PK | 내부 ID |
| `measurement_code` | varchar(80) | UK | 예: `P_VALUE`, `KS_STATISTIC` |
| `canonical_name` | text | UK | 표준 측정값 이름 |
| `measurement_category` | varchar(80) | IDX | `statistical_test`, `distance`, `alarm`, `metadata` |
| `value_type` | varchar(50) | IDX | `float`, `integer`, `boolean`, `category`, `json` |
| `unit` | varchar(50) |  | 단위 |
| `higher_is_more_drift` | boolean |  | 값 증가 방향 해석 |
| `valid_range_text` | text |  | 값 범위 설명 |
| `interpretation_text` | text |  | 해석 설명 |
| `caution_text` | text |  | 과잉 해석 방지 |

제약:

```sql
unique(measurement_code)
unique(canonical_name)
```

### 6.2 `variant_measurement`

variant가 산출하는 측정값 연결이다.

| 컬럼 | 타입 | Key | 설명 |
|---|---|---|---|
| `variant_measurement_id` | bigint | PK | 내부 ID |
| `method_variant_id` | bigint | FK, IDX | method-variant |
| `measurement_id` | bigint | FK, IDX | canonical measurement |
| `raw_measurement_name` | text | IDX | 원문/라이브러리 산출명 |
| `is_primary` | boolean | IDX | 핵심 산출값 여부 |
| `required_for_report` | boolean | IDX | 보고서 필수 여부 |
| `interpretation_override_text` | text |  | method context별 해석 보정 |
| `source_document_id` | bigint | FK | 원천 문서/CSV |

제약:

```sql
unique(method_variant_id, measurement_id, raw_measurement_name)
```

### 6.3 `parameter`

표준 파라미터 catalog다.

| 컬럼 | 타입 | Key | 설명 |
|---|---|---|---|
| `parameter_id` | bigint | PK | 내부 ID |
| `parameter_code` | varchar(100) | UK | 예: `reference_window`, `threshold_or_alpha` |
| `display_name` | text |  | 표시명 |
| `value_type` | varchar(50) | IDX | `float`, `integer`, `string`, `enum`, `json`, `window` |
| `default_value_text` | text |  | 기본값 |
| `allowed_values_json` | jsonb |  | enum 또는 범위 |
| `description_text` | text |  | 의미 |
| `tuning_effect_text` | text |  | 조절 효과 |

### 6.4 `variant_parameter`

variant별 사용 파라미터 연결이다.

| 컬럼 | 타입 | Key | 설명 |
|---|---|---|---|
| `variant_parameter_id` | bigint | PK | 내부 ID |
| `method_variant_id` | bigint | FK, IDX | method-variant |
| `parameter_id` | bigint | FK, IDX | parameter |
| `is_required` | boolean | IDX | 필수 여부 |
| `default_value_text` | text |  | variant별 기본값 |
| `allowed_values_json` | jsonb |  | variant별 허용값 |
| `parameter_role` | varchar(80) | IDX | `input`, `threshold`, `window`, `preprocessing`, `policy` |
| `caution_text` | text |  | 주의사항 |
| `source_document_id` | bigint | FK | 원천 문서/CSV |

제약:

```sql
unique(method_variant_id, parameter_id)
```

## 7. Chart Catalog

### 7.1 `chart_definition`

chart id와 차트 의미를 관리한다.

| 컬럼 | 타입 | Key | 설명 |
|---|---|---|---|
| `chart_definition_id` | bigint | PK | 내부 ID |
| `chart_code` | varchar(80) | UK | 예: `CHART-EDF-001` |
| `chart_family` | varchar(80) | IDX | `EDF`, `ERR`, `MV`, `TEXT` 등 |
| `display_title` | text |  | 차트 제목 |
| `purpose_text` | text |  | 차트 목적 |
| `component_summary_text` | text |  | 주요 구성 |
| `input_contract_json` | jsonb |  | 렌더러 입력 스키마 요약 |
| `output_contract_json` | jsonb |  | PNG/HTML 등 출력 스키마 |
| `status` | varchar(20) | IDX | `draft`, `active`, `deprecated` |
| `source_document_id` | bigint | FK | chart guide 원천 |

제약:

```sql
unique(chart_code)
check(status in ('draft','active','deprecated'))
```

### 7.2 `variant_chart`

method-variant와 chart 연결이다.

| 컬럼 | 타입 | Key | 설명 |
|---|---|---|---|
| `variant_chart_id` | bigint | PK | 내부 ID |
| `method_variant_id` | bigint | FK, IDX | method-variant |
| `chart_definition_id` | bigint | FK, IDX | chart |
| `is_primary_chart` | boolean | IDX | 기본 차트 여부 |
| `selection_reason_text` | text |  | 연결 이유 |
| `display_order` | integer |  | 표시 순서 |
| `source_document_id` | bigint | FK | chart guide |

제약:

```sql
unique(method_variant_id, chart_definition_id)
```

### 7.3 `chart_asset`

현재 HTML/CSS/JS/PNG 같은 차트 산출물을 관리한다.

| 컬럼 | 타입 | Key | 설명 |
|---|---|---|---|
| `chart_asset_id` | bigint | PK | 내부 ID |
| `chart_definition_id` | bigint | FK, IDX | chart |
| `asset_type` | varchar(30) | IDX | `html`, `css`, `js`, `png`, `description_html` |
| `asset_path` | text | UK | 저장소 기준 상대 경로 |
| `checksum_sha256` | char(64) | IDX | 내용 해시 |
| `is_generated` | boolean | IDX | 생성 산출물 여부 |
| `created_at` | timestamptz |  | 생성 시각 |

제약:

```sql
unique(asset_path)
unique(chart_definition_id, asset_type, asset_path)
```

### 7.4 `chart_component`

chart를 구성하는 재사용 component의 의미와 해석 기준을 관리한다. 원천은 `../chart_builder/docs/chart_components/*.md`다.

| 컬럼 | 타입 | Key | 설명 |
|---|---|---|---|
| `chart_component_id` | bigint | PK | 내부 ID |
| `component_code` | varchar(120) | UK | 예: `bar_chart`, `threshold_line` |
| `display_name` | text |  | 표시명 |
| `purpose_text` | text |  | component 목적 |
| `shows_text` | text |  | 화면에서 보여주는 정보 |
| `interpretation_text` | text |  | 파라미터/표현 변경에 따른 해석 방법 |
| `caution_text` | text |  | 렌더링/해석 주의사항 |
| `input_contract_json` | jsonb |  | 입력 데이터 계약 예시 |
| `config_schema_json` | jsonb |  | 주요 설정 파라미터 목록 |
| `renderer_status` | varchar(20) | IDX | `draft`, `active`, `deprecated` |
| `source_document_id` | bigint | FK | component 설명 문서 |

제약:

```sql
unique(component_code)
check(renderer_status in ('draft','active','deprecated'))
```

### 7.5 `chart_component_usage`

어떤 chart가 어떤 component를 사용하는지 관리한다. 원천은 `../chart_builder/docs/chart_component_to_chart.csv`다.

| 컬럼 | 타입 | Key | 설명 |
|---|---|---|---|
| `chart_component_usage_id` | bigint | PK | 내부 ID |
| `chart_definition_id` | bigint | FK, IDX | chart |
| `chart_component_id` | bigint | FK, IDX | component |
| `usage_role` | varchar(80) |  | 사용 역할. 기본값은 `declared_component` |
| `display_order` | integer |  | chart 내 component 표시 순서 |
| `usage_reason_text` | text |  | 사용 이유 |
| `source_document_id` | bigint | FK | component-chart 매핑 CSV |

제약:

```sql
unique(chart_definition_id, chart_component_id, usage_role)
```

### 7.6 `chart_component_raw_mapping`

원본 chart 분석에서 추출된 자유 텍스트 component 표현을 보존한다. 원천은 `../chart_builder/docs/chart_component_raw_to_chart.csv`다.

| 컬럼 | 타입 | Key | 설명 |
|---|---|---|---|
| `chart_component_raw_mapping_id` | bigint | PK | 내부 ID |
| `chart_definition_id` | bigint | FK, IDX | chart |
| `raw_component_text` | text |  | 원본에서 추출한 component 표현 |
| `normalized_component_id` | bigint | FK, nullable | 정규 component로 직접 매핑되는 경우의 component |
| `source_document_id` | bigint | FK | raw component 매핑 CSV |

제약:

```sql
unique(chart_definition_id, raw_component_text)
```

### 7.7 `chart_component_interpretation_rule`

component가 그리는 그래프를 어떤 시각적 근거로 해석할지 관리한다. 이 테이블은 원자료 요약이 아니라, "기준선 미초과지만 최근 기준선 접촉 이력이 있어 위험하다"처럼 그래프의 판단 구조를 문장화하기 위한 규칙을 저장한다.

| 컬럼 | 타입 | Key | 설명 |
|---|---|---|---|
| `chart_component_interpretation_rule_id` | bigint | PK | 내부 ID |
| `chart_component_id` | bigint | FK, IDX | component |
| `rule_code` | varchar(120) | UK(part) | 규칙 코드. 예: `BELOW_THRESHOLD_BUT_NEAR_OR_RECENT_TOUCH` |
| `signal_type` | varchar(120) | IDX | 규칙이 읽는 시각 신호 유형 |
| `condition_json` | jsonb |  | latest, threshold, recent_max, slope 등 조건 구조 |
| `severity_mapping_json` | jsonb |  | normal/watch/candidate 등 판단 단계 설명 |
| `interpretation_template_text` | text |  | LLM이 결과값을 끼워 넣어 쓸 해석 문장 템플릿 |
| `caution_text` | text |  | 과잉 해석 방지 문구 |
| `source_document_id` | bigint | FK | 기준 component 문서 |

제약:

```sql
unique(chart_component_id, rule_code)
```

### 7.8 `chart_interpretation_guide`

chart 안의 여러 component 해석을 어떤 순서와 논리로 종합할지 관리한다. 이 테이블은 component별 판독 결과를 단순 나열하지 않고, chart 목적과 drift 판단 기준에 맞춰 현재 상황 해석 문장을 만들기 위한 상위 가이드다.

| 컬럼 | 타입 | Key | 설명 |
|---|---|---|---|
| `chart_interpretation_guide_id` | bigint | PK | 내부 ID |
| `chart_definition_id` | bigint | FK, IDX | chart |
| `guide_code` | varchar(120) | UK(part) | 가이드 코드. 기본값은 `DEFAULT_SYNTHESIS` |
| `interpretation_flow_json` | jsonb |  | component/section 판독 순서 |
| `synthesis_rule_json` | jsonb |  | 목적, 구성, 해석 순서, 판단 기준, 금지 해석 section 묶음 |
| `interpretation_template_text` | text |  | LLM이 chart 전체 해석을 작성할 때 쓰는 종합 템플릿 |
| `caution_text` | text |  | chart-level 과잉 해석 방지 문구 |
| `source_document_id` | bigint | FK | chart 해석 문서 |

제약:

```sql
unique(chart_definition_id, guide_code)
```

## 8. 문서 지식 테이블

### 8.1 `document_section`

Markdown을 section 단위로 분해한 테이블이다. 원문 전체가 아니라 운영 단위 section을 저장한다.

| 컬럼 | 타입 | Key | 설명 |
|---|---|---|---|
| `document_section_id` | bigint | PK | 내부 ID |
| `source_document_id` | bigint | FK, IDX | 원천 문서 |
| `section_key` | varchar(160) | UK | 안정 section key |
| `section_type` | varchar(80) | IDX | `purpose`, `components`, `interpretation_steps`, `caution`, `variant_detail`, `selection_rule` |
| `heading_text` | text |  | heading 원문 |
| `heading_level` | integer |  | Markdown heading level |
| `body_markdown` | text |  | section 본문 markdown |
| `body_plain_text` | text | FTS | 검색용 plain text |
| `body_html` | text |  | 렌더링 cache |
| `line_start` | integer |  | 원천 시작 line |
| `line_end` | integer |  | 원천 종료 line |
| `content_hash` | char(64) | IDX | section 내용 해시 |
| `display_order` | integer | IDX | 문서 내 순서 |
| `is_active` | boolean | IDX | 현재 활성 section 여부 |

제약:

```sql
unique(source_document_id, section_key)
```

권장 section type:

| 값 | 설명 |
|---|---|
| `chart_purpose` | 차트 목적 |
| `chart_components` | 차트 구성 |
| `interpretation_steps` | 해석 순서 |
| `drift_decision_criteria` | drift 후보 판단 기준 |
| `example_interpretation` | 예시 차트 해석 |
| `forbidden_interpretation` | 금지 해석 |
| `additional_checks` | 추가 확인 항목 |
| `suitable_use_cases` | 적합한 사용 대상 |
| `variant_detail` | algorithm variant 상세 |
| `selection_rule` | 추천 선택 규칙 |
| `parameter_explanation` | 파라미터 설명 |
| `measurement_interpretation` | 측정값 해석 |

### 8.2 `section_entity_link`

section이 어떤 chart/method/variant/measurement/parameter와 연결되는지 저장한다.

| 컬럼 | 타입 | Key | 설명 |
|---|---|---|---|
| `section_entity_link_id` | bigint | PK | 내부 ID |
| `document_section_id` | bigint | FK, IDX | section |
| `entity_type` | varchar(40) | IDX | `chart`, `component`, `method`, `variant`, `method_variant`, `measurement`, `parameter` |
| `entity_id` | bigint | IDX | 대상 entity의 내부 ID |
| `link_role` | varchar(80) | IDX | `describes`, `warns`, `recommends`, `explains_output`, `explains_parameter` |
| `confidence` | numeric(5,4) |  | parser confidence |

제약:

```sql
unique(document_section_id, entity_type, entity_id, link_role)
```

주의: `entity_id`는 polymorphic FK이므로 DB 차원 FK 대신 application validation 또는 별도 link table 분리를 선택할 수 있다. 운영에서 FK 엄격성이 더 중요하면 아래처럼 분리한다.

```text
chart_document_section
method_document_section
variant_document_section
measurement_document_section
parameter_document_section
```

## 9. 알고리즘 구현/실행 테이블

### 9.1 `algorithm_implementation`

실제로 실행 가능한 알고리즘 구현체를 등록한다.

| 컬럼 | 타입 | Key | 설명 |
|---|---|---|---|
| `algorithm_implementation_id` | bigint | PK | 내부 ID |
| `method_variant_id` | bigint | FK, IDX | 구현 대상 variant |
| `implementation_code` | varchar(120) | UK | 예: `scipy_ks_2samp_v1` |
| `runtime_type` | varchar(40) | IDX | `python`, `sql`, `service`, `notebook` |
| `module_path` | text |  | Python module path |
| `callable_name` | text |  | 함수/클래스 이름 |
| `input_schema_json` | jsonb |  | 입력 스키마 |
| `output_schema_json` | jsonb |  | 출력 스키마 |
| `default_params_json` | jsonb |  | 기본 파라미터 |
| `version` | varchar(40) | IDX | 구현 버전 |
| `status` | varchar(20) | IDX | `draft`, `active`, `deprecated` |
| `created_at` | timestamptz |  | 생성 시각 |

제약:

```sql
unique(implementation_code)
unique(method_variant_id, implementation_code, version)
```

### 9.2 `algorithm_run`

알고리즘 실행 단위다.

| 컬럼 | 타입 | Key | 설명 |
|---|---|---|---|
| `algorithm_run_id` | bigint | PK | 내부 ID |
| `algorithm_implementation_id` | bigint | FK, IDX | 실행 구현체 |
| `run_key` | varchar(160) | UK | 외부 추적용 실행 키 |
| `dataset_ref` | text | IDX | 입력 데이터 참조 |
| `reference_window_ref` | text | IDX | reference window |
| `current_window_ref` | text | IDX | current window |
| `input_signal` | varchar(80) | IDX | `feature`, `score`, `error_rate`, `embedding` 등 |
| `target_feature` | text | IDX | feature/metric 이름 |
| `params_json` | jsonb |  | 실행 파라미터 |
| `run_status` | varchar(20) | IDX | `queued`, `running`, `success`, `failed`, `cancelled` |
| `started_at` | timestamptz | IDX | 시작 시각 |
| `finished_at` | timestamptz |  | 종료 시각 |
| `error_message` | text |  | 실패 메시지 |

제약:

```sql
unique(run_key)
check(run_status in ('queued','running','success','failed','cancelled'))
```

### 9.3 `algorithm_result`

실행 결과 측정값을 long format으로 저장한다.

| 컬럼 | 타입 | Key | 설명 |
|---|---|---|---|
| `algorithm_result_id` | bigint | PK | 내부 ID |
| `algorithm_run_id` | bigint | FK, IDX | 실행 |
| `measurement_id` | bigint | FK, IDX | 측정값 |
| `raw_measurement_name` | text | IDX | 구현체 산출명 |
| `value_float` | double precision | IDX | 숫자 결과 |
| `value_text` | text |  | 문자열/범주 결과 |
| `value_bool` | boolean | IDX | boolean 결과 |
| `value_json` | jsonb |  | 복합 결과 |
| `unit` | varchar(50) |  | 단위 |
| `is_primary` | boolean | IDX | 주요 결과 여부 |
| `created_at` | timestamptz |  | 생성 시각 |

제약:

```sql
unique(algorithm_run_id, measurement_id, raw_measurement_name)
```

## 10. 차트 렌더링 테이블

### 10.1 `chart_render_job`

알고리즘 결과를 사용해 차트를 생성하는 작업이다.

| 컬럼 | 타입 | Key | 설명 |
|---|---|---|---|
| `chart_render_job_id` | bigint | PK | 내부 ID |
| `chart_definition_id` | bigint | FK, IDX | chart |
| `algorithm_run_id` | bigint | FK, IDX | 기반 실행 결과 |
| `render_key` | varchar(160) | UK | 외부 추적용 렌더 키 |
| `renderer_type` | varchar(40) | IDX | `html_js`, `python`, `service` |
| `renderer_version` | varchar(40) |  | 렌더러 버전 |
| `input_payload_json` | jsonb |  | 렌더 입력 |
| `render_status` | varchar(20) | IDX | `queued`, `running`, `success`, `failed` |
| `started_at` | timestamptz | IDX | 시작 시각 |
| `finished_at` | timestamptz |  | 종료 시각 |
| `error_message` | text |  | 실패 메시지 |

### 10.2 `chart_render_output`

렌더링 결과물이다.

| 컬럼 | 타입 | Key | 설명 |
|---|---|---|---|
| `chart_render_output_id` | bigint | PK | 내부 ID |
| `chart_render_job_id` | bigint | FK, IDX | 렌더 job |
| `output_type` | varchar(30) | IDX | `html`, `png`, `svg`, `json`, `thumbnail` |
| `output_path` | text | UK | 파일 경로 또는 object storage key |
| `mime_type` | varchar(80) |  | MIME type |
| `checksum_sha256` | char(64) | IDX | 결과물 해시 |
| `created_at` | timestamptz |  | 생성 시각 |

## 11. 주요 ER 관계

```text
drift_method 1 --- N method_variant N --- 1 algorithm_variant
method_variant 1 --- N variant_measurement N --- 1 measurement
method_variant 1 --- N variant_parameter N --- 1 parameter
method_variant 1 --- N variant_chart N --- 1 chart_definition
chart_definition 1 --- N chart_component_usage N --- 1 chart_component
chart_definition 1 --- N chart_component_raw_mapping N --- 0..1 chart_component
chart_definition 1 --- N chart_interpretation_guide
chart_component 1 --- N chart_component_interpretation_rule

source_document 1 --- N document_section
document_section N --- N chart/component/method/variant/measurement/parameter

method_variant 1 --- N algorithm_implementation
algorithm_implementation 1 --- N algorithm_run
algorithm_run 1 --- N algorithm_result

chart_definition 1 --- N chart_render_job
algorithm_run 1 --- N chart_render_job
chart_render_job 1 --- N chart_render_output
```

## 12. Import 매핑

| 현재 파일 | 대상 테이블 |
|---|---|
| `drift_methods_catalog.md` | `drift_method`, `source_document`, `document_section` |
| `algorithm_variants/*_algorithm_variants.md` | `algorithm_variant`, `method_variant`, `document_section`, `section_entity_link` |
| `drift_method_variant_links.csv` | `method_variant` |
| `drift_measurements_catalog.csv` | `measurement` |
| `drift_method_variant_measurement_links.csv` | `variant_measurement` |
| `drift_method_variant_measurement_summary.csv` | 검증용 summary. 필요 시 materialized view |
| `drift_measurement_to_methods.csv` | 검증용 역인덱스. 필요 시 materialized view |
| `drift_method_variant_parameters.csv` | `parameter`, `variant_parameter` |
| `chart_docs/drift_method_variant_chart_guide.md` | `chart_definition`, `variant_chart`, `document_section` |
| `chart_docs/drift_chart_interpretation_*.md` | `document_section`, `section_entity_link` |
| `chart_docs/drift_chart_interpretation_*.md` | `chart_interpretation_guide` |
| `charts/chart_*.html/css/js` | `chart_asset` |
| `charts/output/CHART-*.png` | `chart_asset` |
| `../chart_builder/docs/chart_components/*.md` | `chart_component`, `source_document`, `document_section`, `section_entity_link` |
| `../chart_builder/docs/chart_component_to_chart.csv` | `chart_component_usage` |
| `../chart_builder/docs/chart_component_raw_to_chart.csv` | `chart_component_raw_mapping` |
| importer 내 visual rule seed | `chart_component_interpretation_rule` |

## 13. 권장 인덱스

```sql
create index idx_method_category on drift_method(method_category);
create index idx_variant_family on algorithm_variant(variant_family);
create index idx_method_variant_method on method_variant(drift_method_id);
create index idx_variant_measurement_measurement on variant_measurement(measurement_id);
create index idx_variant_parameter_parameter on variant_parameter(parameter_id);
create index idx_chart_family on chart_definition(chart_family);
create index idx_variant_chart_chart on variant_chart(chart_definition_id);
create index idx_chart_component_usage_chart on chart_component_usage(chart_definition_id);
create index idx_chart_component_usage_component on chart_component_usage(chart_component_id);
create index idx_chart_component_raw_chart on chart_component_raw_mapping(chart_definition_id);
create index idx_chart_component_rule_component on chart_component_interpretation_rule(chart_component_id);
create index idx_chart_component_rule_signal on chart_component_interpretation_rule(signal_type);
create index idx_chart_interpretation_guide_chart on chart_interpretation_guide(chart_definition_id);
create index idx_document_section_type on document_section(section_type);
create index idx_document_section_source_order on document_section(source_document_id, display_order);
create index idx_section_entity on section_entity_link(entity_type, entity_id);
create index idx_algorithm_run_status_started on algorithm_run(run_status, started_at);
create index idx_algorithm_result_run_measurement on algorithm_result(algorithm_run_id, measurement_id);
create index idx_chart_render_status_started on chart_render_job(render_status, started_at);
```

PostgreSQL full-text search를 쓰는 경우:

```sql
create index idx_document_section_fts
on document_section
using gin(to_tsvector('simple', coalesce(body_plain_text, '')));
```

## 14. 삭제/변경 정책

1. catalog entity는 가능하면 물리 삭제하지 않고 `status='deprecated'` 또는 `is_active=false`로 비활성화한다.
2. source 문서에서 사라진 section은 `is_active=false`로 남긴다.
3. 실행 결과(`algorithm_run`, `algorithm_result`)는 감사와 재현성을 위해 기본적으로 삭제하지 않는다.
4. chart render output은 파일 보존 정책에 따라 삭제할 수 있지만, metadata row는 남긴다.
5. import batch 단위로 변경 diff를 기록한다.

## 15. 구현 순서

1. catalog schema 생성
2. CSV import 구현
3. Markdown parser 구현
4. `source_document`, `document_section`, `section_entity_link` import
5. 웹 갤러리를 RDB 조회 기반으로 전환
6. algorithm implementation registry 추가
7. algorithm run/result 저장
8. chart render job/output 저장
9. 검색 API와 추천 API 구현

## 16. 최소 MVP 스키마

처음부터 모든 테이블을 구현하지 않을 경우 아래만 먼저 만든다.

```text
source_document
drift_method
algorithm_variant
method_variant
measurement
variant_measurement
parameter
variant_parameter
chart_definition
variant_chart
document_section
section_entity_link
```

이 MVP만으로도 현재 CSV/Markdown 지식베이스를 RDB 기반으로 조회할 수 있다. 실제 실행과 렌더링은 이후 `algorithm_*`, `chart_render_*` 테이블을 추가해 확장한다.

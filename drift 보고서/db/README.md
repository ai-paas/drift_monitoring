# Drift DB 구축 방법

이 폴더는 drift 모니터링 catalog와 문서 section을 PostgreSQL에 적재하기 위한 DB 스키마와 import 스크립트를 담는다.

## 대상 DB

Docker Desktop의 PostgreSQL 컨테이너를 사용한다.

```text
container: lci-postgres
database: drift_monitoring
user: postgres
```

## DB 생성

```powershell
docker exec lci-postgres createdb -U postgres drift_monitoring
```

이미 DB가 있으면 이 명령은 실패할 수 있다. 그 경우 다음 단계부터 진행한다.

## 스키마 적용

```powershell
docker cp db\schema.sql lci-postgres:/tmp/drift_schema.sql
docker exec lci-postgres psql -U postgres -d drift_monitoring -v ON_ERROR_STOP=1 -f /tmp/drift_schema.sql
```

## 데이터 적재 SQL 생성

```powershell
python db\import_drift_db.py
```

이 명령은 `db/load_data.sql`을 생성한다. `load_data.sql`은 현재 Markdown/CSV에서 재생성되는 로컬 산출물이므로 Git에는 등록하지 않는다.

## 데이터 적재

```powershell
docker cp db\load_data.sql lci-postgres:/tmp/drift_load_data.sql
docker exec lci-postgres psql -U postgres -d drift_monitoring -v ON_ERROR_STOP=1 -f /tmp/drift_load_data.sql
```

## 검증 쿼리

```powershell
docker exec lci-postgres psql -U postgres -d drift_monitoring -c "select 'drift_method' table_name, count(*) from drift_method union all select 'algorithm_variant', count(*) from algorithm_variant union all select 'chart_definition', count(*) from chart_definition union all select 'chart_component', count(*) from chart_component union all select 'chart_component_usage', count(*) from chart_component_usage union all select 'chart_component_interpretation_rule', count(*) from chart_component_interpretation_rule union all select 'chart_interpretation_guide', count(*) from chart_interpretation_guide union all select 'document_section', count(*) from document_section;"
```

현재 기준 주요 적재 건수:

```text
drift_method: 57
algorithm_variant: 177
method_variant: 177
measurement: 42
variant_measurement: 485
parameter: 215
variant_parameter: 1661
chart_definition: 53
variant_chart: 188
chart_asset: 265
chart_component: 32
chart_component_usage: 350
chart_component_raw_mapping: 448
chart_component_interpretation_rule: 34
chart_interpretation_guide: 53
document_section: 2002
section_entity_link: 2112
```

# Drift Monitoring Framework

추론 데이터의 변화 감지, 이벤트 분석 차트와 근거 기반 자연어 해석을 연결하는 개발용 프레임워크입니다. 현재 Linux 컨테이너가 사용하는 소스를 정리한 최초 공개본입니다.

## 구성

| 구성 | 역할 |
| --- | --- |
| drift_algorithm_impl | 통계 검정·거리·스트리밍 탐지·적응 방법 |
| drift_control_plane | Admin, Drift Server, Test Feeder, SQLite 기록·관리 계약 |
| drift_metric_timeseries | 시계열 관찰과 이벤트 상세 분석 UI |
| chart_runtime | 차트 payload 및 공용 렌더러 |
| chart_builder | 레이아웃·컴포넌트·데이터 연결 편집 |
| drift 보고서 | 카탈로그 CSV/Markdown, PostgreSQL 스키마·갤러리 |
| llm_interpretation_server | 차트 근거와 가이드에 기반한 LLM 해석 |
| 테스트데이터 | 합성 자료 생성기와 시나리오 문서 |
| ADL | 계약·상태·구조 검증용 설계 자산 |

카탈로그의 56개 기본 방법과 Generic/Fallback 항목, 차트 53개를 포함합니다. 등록·구현·실행 검증 범위는 다르므로 개별 설계와 [검증 기록](docs/IMPORT_VALIDATION.md)을 확인하세요.

## Docker 실행

Docker Engine와 Compose v2가 필요합니다. 실행할 호스트에서 다음을 수행합니다.

```bash
cp .env.example .env
# .env에서 POSTGRES_PASSWORD, LLM_API_ENDPOINT, LLM_MODEL 등을 설정
# 실제 비밀번호·API 키는 .env에만 보관
docker compose up -d --build
```

PostgreSQL이 준비된 뒤 최초 한 번 카탈로그를 초기화합니다.

```bash
docker compose exec drift-llm-postgres pg_isready -U postgres -d drift_monitoring
docker compose exec drift-llm-postgres psql -U postgres -d drift_monitoring -v ON_ERROR_STOP=1 -f '/opt/drift_llm_intepretation/drift 보고서/db/schema.sql'
docker compose exec drift-llm-postgres python3 '/opt/drift_llm_intepretation/drift 보고서/db/import_drift_db.py'
docker compose exec drift-llm-postgres psql -U postgres -d drift_monitoring -v ON_ERROR_STOP=1 -f '/opt/drift_llm_intepretation/drift 보고서/db/load_data.sql'
```

LLM 해석 지식 테이블은 기존 개발 DB에서 별도 관리됐습니다. 빈 DB에서는 [배포 문서의 기존 테이블 생성 예시](docs/DEPLOYMENT.md#existing-interpretation-tables)를 실행한 후 가이드를 등록하세요. 이 문서 예시는 기존 테이블 구조를 설명하며 새 마이그레이션·관리 계약을 추가하지 않습니다.

| 화면 | 로컬 주소 |
| --- | --- |
| Admin·모니터링 진입 | http://localhost:8770/admin |
| Chart Builder | http://localhost:8766/builder_prototype.html |
| Chart Gallery | http://localhost:8765/gallery.html |
| LLM API 문서 | http://localhost:8767/docs |

Drift(8771)와 Test Feeder(8772)는 컨테이너 내부에서만 실행합니다. 표준 Compose의 소스는 이미지에 포함됩니다. Linux 개발용 bind mount가 필요하면 docker-compose.linux.yml을 사용하고 같은 파일 지정으로 모든 후속 명령을 실행하세요. 기존 운영 볼륨과는 자동 연결하지 않습니다. 자세한 저장·연결 경계는 [배포 설명](docs/DEPLOYMENT.md)을 참고하세요.

## 합성 자료와 테스트

실제 DB 추출 자료, DB 백업·SQLite, LLM 실행 기록, 다운로드 묶음과 원본 Word 보고서는 공개본에 포함하지 않습니다. 기존 등록 데이터나 이벤트도 자동 복원되지 않습니다. 예를 들어 합성 CASE-001 자료는 다음으로 생성합니다.

```bash
python3 테스트데이터/generate_case_data.py --case CASE-001
```

Python 테스트 환경에서는 requirements.docker.txt와 pytest를 설치한 후 실행합니다.

```bash
PYTHONPATH=.:drift_control_plane:drift_algorithm_impl python3 -m pytest -q drift_algorithm_impl/tests
PYTHONPATH=.:drift_control_plane:drift_algorithm_impl python3 -m pytest -q drift_control_plane/tests/test_payload_adapter_catalog_coverage.py drift_control_plane/tests/test_payload_adapter_binding.py llm_interpretation_server/test_interpretation_regressions.py
python3 chart_runtime/tests/validate_payload_registry.py
```

Builder 브라우저 테스트는 Node.js, playwright-core와 Chrome을 준비한 후 실행합니다. BUILDER_URL로 별도 테스트 인스턴스를 지정할 수 있습니다.

```bash
node chart_builder/tests/placement_browser_test.cjs
node chart_builder/tests/all_components_browser_test.cjs
```

알려진 실패와 경고는 [최초 등록 검증 기록](docs/IMPORT_VALIDATION.md)에 명시했습니다. 테스트와 라이브 LLM/운영 배포 검증을 구분합니다. 지연·부분 라벨의 예측 매칭과 후행 재집계 서버는 아직 제공하지 않습니다.

## 변경 규칙

[CODEX_DEVELOPMENT_GUIDE.md](CODEX_DEVELOPMENT_GUIDE.md)와 [managed contract 목록](drift_control_plane/managed_contracts.csv)을 따릅니다. P0 항목 변경에는 사전 동의가 필요합니다. 실제 관측값·설명과 탐지·원인 확정을 구분합니다.

## License

이 저장소의 기존 [Apache License 2.0](LICENSE)을 유지합니다. 의존 라이브러리의 라이선스와 외부 모델·데이터의 이용 조건은 별도로 확인해야 합니다.

# Drift Monitoring Framework

**AI 모델의 입력·출력 변화를 감지하고, 이벤트의 근거를 차트와 자연어로 확인하는 모니터링 프레임워크입니다.**

숫자·범주·임베딩·오류 신호를 분석하는 알고리즘, 실행을 조율하는 관리 서버, 시계열·상세 분석 UI, 차트 Builder와 LLM 해석 서비스를 제공합니다. 현재 공개본은 Linux 통합 컨테이너에서 사용한 소스를 정리한 개발·데모용 버전입니다.

[빠른 시작](#빠른-시작) · [구성](#시스템-구성) · [화면 주소](#화면과-api) · [테스트](#테스트) · [문서](#관련-문서)

## 주요 기능

| 기능 | 설명 |
| --- | --- |
| 자료 연계·재생 | 관측 자료를 읽고 합성 테스트 자료를 논리 시간에 따라 재생 |
| 변화 감지 | 기준·현재 구간 또는 시간순 신호를 비교해 통계량·거리·경보 생성 |
| 시계열 모니터링 | 기간·지표를 탐색하고 관심 이벤트 선택 |
| 이벤트 상세 분석 | 분포·추세·요약 수치 등 이벤트의 근거 표시 |
| 차트 설계 | 레이아웃·컴포넌트·속성·데이터 연결 편집과 미리보기 |
| 근거 기반 해석 | 차트 데이터와 해석 가이드를 LLM에 전달해 설명 생성 |
| 계약 관리 | 알고리즘·API·payload·Runtime의 관리 계약과 검증 자료 유지 |

처리 흐름은 **자료 준비 → 구간 집계 → 탐지·이벤트 기록 → 사용자 선택 → 상세 차트 → 선택적 LLM 설명**입니다. 차트 설계와 해석 지식 관리는 이 흐름을 지원합니다. LLM이 탐지 계산이나 원인 확정을 대신하지 않습니다.

## 알고리즘과 차트

기본 카탈로그는 56개 방법을 다음 8개 범주로 구분합니다. DB에는 별도 Generic/Fallback 항목도 등록됩니다.

| 분류 | 관찰 대상 | 기본 방법 수 |
| --- | --- | ---: |
| 구간 분포 비교 | 기준·현재의 숫자·범주·벡터 분포 차이 | 25 |
| 스트리밍 변화 감지 | 시간순 지표의 변화 시점·누적 신호 | 9 |
| 정답·오류 기반 감지 | 예측 오류와 성능 변화 | 7 |
| 다변량 공정 관리 | 여러 숫자 지표의 결합 변화 | 3 |
| 표현·불확실성 변화 | 임베딩·특성 표현·confidence·entropy | 6 |
| 설명·판단 근거 변화 | SHAP 기여도·트리 분기 근거 | 2 |
| 기간 구분 모델 | 기준·현재 자료의 구분 가능성 | 2 |
| 운영 적응 | 감지 이후 대체 트리·재학습 평가 | 2 |

차트 정의는 53개, Builder 팔레트는 32종입니다. 공용 Runtime의 명시 구성요소 37종과 Builder의 합집합은 코드 기준 41종입니다. 별칭과 공용·기본 카드 경로를 포함하므로 전용 렌더러 41개를 의미하지 않습니다. **카탈로그 등록, 실제 구현, 현재 검증 범위는 구분**하며 [최초 등록 검증 기록](docs/IMPORT_VALIDATION.md)에 알려진 상태를 명시했습니다.

## 시스템 구성

| 폴더 | 역할 |
| --- | --- |
| `drift_algorithm_impl/` | 알고리즘 구현·단위 테스트·방법별 설계 |
| `drift_control_plane/` | Admin / Drift / Test Feeder, API, SQLite 기록·관리 계약 |
| `drift_metric_timeseries/` | 시계열 관찰·이벤트 상세 분석 UI |
| `chart_runtime/` | 차트 payload 정의와 공용 브라우저 렌더링 |
| `chart_builder/` | 차트·레이아웃 편집과 저장·미리보기 |
| `drift 보고서/` | CSV·Markdown 카탈로그, PostgreSQL 스키마·갤러리 |
| `llm_interpretation_server/` | 차트·컴포넌트의 근거 기반 설명 |
| `테스트데이터/` | 합성 자료 생성기와 테스트 시나리오 문서 |
| `ADL/` | 계약·상태·구조 검증용 설계 자산 |
| `docker/` | 통합 프로세스 실행 설정 |

하나의 Docker 컨테이너에서 Supervisor가 PostgreSQL과 각 서버 프로세스를 실행합니다. 시각화는 사용자 브라우저에서 수행하고 LLM은 별도 endpoint를 사용합니다.

| 저장 위치 | 내용 | 표준 Compose에서의 보존 |
| --- | --- | --- |
| PostgreSQL | 방법·차트 정의, 문서·해석 지식 | 프로젝트 전용 named volume |
| SQLite | 관측·집계·탐지 실행·이벤트 | 기본적으로 컨테이너 쓰기 계층 |
| Builder JSON | 저장 차트·레이아웃 | 기본적으로 컨테이너 쓰기 계층 |

표준 Compose에서는 컨테이너를 재생성할 때 SQLite·Builder 변경이 사라질 수 있습니다. Linux 개발용 Compose는 소스 폴더를 bind mount하므로 해당 파일을 호스트에 유지합니다. 운영 보존이 필요하면 별도의 저장·백업 구성을 검토하세요.

## 빠른 시작

### 1. 저장소와 환경 설정

Git, Docker Engine, Docker Compose v2가 필요합니다. 아래 명령은 Bash 기준입니다.

```bash
git clone https://github.com/ai-paas/drift_monitoring.git
cd drift_monitoring
cp .env.example .env
```

`.env`의 값을 실제 환경에 맞게 수정합니다.

| 변수 | 설정 내용 |
| --- | --- |
| `POSTGRES_PASSWORD` | 새 DB에서 사용할 비밀번호. 예시 값을 변경 |
| `BIND_ADDRESS` | 기본 `127.0.0.1`; 원격 접근 시 실제 바인딩·접근 정책 설정 |
| `LLM_API_ENDPOINT` | 컨테이너에서 접근 가능한 OpenAI 호환 chat completions 주소 |
| `LLM_MODEL` | 해당 endpoint에서 제공하는 모델명 |
| `LLM_API_KEY` | 필요한 경우 API 키, 그 외 빈 값 |
| `LLM_TIMEOUT_SECONDS` / `LLM_RETRY_COUNT` | 요청 대기 시간과 재시도 수 |

`host.docker.internal` 예시는 Docker 호스트의 LLM에 접근하는 경우입니다. 원격 LLM은 그 서버 주소로 바꾸세요. `.env`는 Git 등록 대상에서 제외됩니다.

### 2. 서버 시작

```bash
docker compose up -d --build
docker compose ps
docker compose logs --tail=100
```

### 3. 빈 DB의 카탈로그 초기화

다음 명령은 **새 DB 초기화용**입니다. 기존 운영 DB에 재적용하기 전에는 schema·적재 동작과 백업을 확인하세요.

```bash
docker compose exec drift-llm-postgres pg_isready -U postgres -d drift_monitoring
```

`accepting connections`가 표시되면 스키마와 카탈로그를 적용합니다.

```bash
docker compose exec drift-llm-postgres psql -U postgres -d drift_monitoring -v ON_ERROR_STOP=1 -f '/opt/drift_llm_intepretation/drift 보고서/db/schema.sql'
docker compose exec drift-llm-postgres python3 '/opt/drift_llm_intepretation/drift 보고서/db/import_drift_db.py'
docker compose exec drift-llm-postgres psql -U postgres -d drift_monitoring -v ON_ERROR_STOP=1 -f '/opt/drift_llm_intepretation/drift 보고서/db/load_data.sql'
```

LLM 해석을 사용하려면 [기존 해석 테이블 생성·가이드 등록 절차](docs/DEPLOYMENT.md#existing-interpretation-tables)도 실행하세요. 기존 개발 DB에서 별도로 관리하던 테이블의 구조를 배포 문서에 제시했습니다. 생성된 `load_data.sql`은 CSV·Markdown에서 재생성되는 파일이며 Git에 등록하지 않습니다.

### 4. 화면과 상태 확인

Admin에서 자료 연결과 탐지·분석 차트를 선택하고, 테스트 자료를 준비·재생한 뒤 시계열 화면에서 이벤트를 확인합니다. 카탈로그 초기화만으로 실제 관측·이벤트가 채워지는 것은 아닙니다.

```bash
curl http://localhost:8770/api/admin/health
curl http://localhost:8767/api/health
```

Admin health의 `database:false`는 현재 Admin이 DB를 직접 소유하지 않는 구현값입니다. `driftServer`, `testFeederServer`, `llmServer` 상태를 함께 확인하세요.

## 화면과 API

| 대상 | 로컬 주소·포트 |
| --- | --- |
| Admin·모니터링 진입 | [localhost:8770/admin](http://localhost:8770/admin) |
| Chart Builder | [localhost:8766/builder_prototype.html](http://localhost:8766/builder_prototype.html) |
| Chart Gallery | [localhost:8765/gallery.html](http://localhost:8765/gallery.html) |
| LLM API 문서 | [localhost:8767/docs](http://localhost:8767/docs) |
| PostgreSQL | `localhost:15432` |
| Drift Server | 컨테이너 내부 `127.0.0.1:8771` |
| Test Feeder | 컨테이너 내부 `127.0.0.1:8772` |

원격 서버에 설치한 경우 `localhost`는 설치 서버를 의미합니다. 기본 바인딩은 로컬 접근만 허용하므로 PC 접근에는 바인딩 변경 또는 SSH 터널이 필요합니다. Admin은 개발용 관리 화면이며 운영 인증 gateway를 제공하지 않습니다.

## Linux 개발용 실행

호스트의 소스 변경을 즉시 반영하고 파일 기반 상태를 호스트에 유지하려면 다음 구성을 사용합니다.

```bash
docker compose -f docker-compose.linux.yml up -d --build
docker compose -f docker-compose.linux.yml logs --tail=100
```

초기화·생성·중지 명령에도 같은 `-f docker-compose.linux.yml` 옵션을 사용하세요. 표준 구성과 같은 포트를 사용하므로 동시에 실행하지 않습니다. 두 구성 모두 기존 설치의 외부 PostgreSQL 볼륨에는 자동 연결하지 않습니다.

## 합성 테스트 자료

공개본에는 실제 CASE-019 추출 자료, 운영 DB·백업·SQLite, LLM 실행 기록, 다운로드 ZIP과 원본 Word 보고서를 포함하지 않습니다. 기존 환경의 연결·관측·이벤트를 자동 복원하지 않습니다.

표준 Compose에서 실행 중인 컨테이너 안에 합성 CASE-001을 생성하는 예입니다.

```bash
docker compose exec drift-llm-postgres python3 '/opt/drift_llm_intepretation/테스트데이터/generate_case_data.py' --case CASE-001
```

자료 생성과 Admin에서의 등록·재생은 별도 단계입니다. 호스트에서 직접 생성하려면 Python 환경을 준비하고 `python3 테스트데이터/generate_case_data.py --case CASE-001`을 사용하세요. 표준 Compose는 이미지에 포함된 소스를 사용하므로 호스트에서 생성한 파일은 자동으로 컨테이너에 반영되지 않습니다.

## 테스트

### Python

프로젝트 루트에서 테스트 의존성을 설치한 뒤 실행합니다. Docker는 필요하지 않은 단위 테스트도 있습니다.

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.docker.txt pytest

PYTHONPATH=.:drift_control_plane:drift_algorithm_impl python3 -m pytest -q drift_algorithm_impl/tests
PYTHONPATH=.:drift_control_plane:drift_algorithm_impl python3 -m pytest -q drift_control_plane/tests/test_payload_adapter_catalog_coverage.py drift_control_plane/tests/test_payload_adapter_binding.py llm_interpretation_server/test_interpretation_regressions.py
python3 chart_runtime/tests/validate_payload_registry.py
```

### Builder 브라우저 검증

Node.js·Chrome과 `playwright-core`가 필요합니다. 다른 서비스와 분리한 테스트용 Builder를 권장합니다.

```bash
npm install --no-save --package-lock=false playwright-core
BUILDER_URL=http://localhost:8766/builder_prototype.html node chart_builder/tests/placement_browser_test.cjs
BUILDER_URL=http://localhost:8766/builder_prototype.html node chart_builder/tests/all_components_browser_test.cjs
```

Chrome 경로가 다르면 `CHROME_PATH`를 지정합니다. `npm` 의존성은 `.gitignore`로 제외됩니다.

## 현재 검증 범위와 제한

최초 공개 등록 시 알고리즘 단위 검사 **308개 통과·1개 실패**, 핵심 payload·LLM 회귀 **22개 통과**, 선택 Runtime 검사 **10개 통과**를 확인했습니다. Builder의 32종 컴포넌트와 4개 overlay는 두 화면 폭에서 검증했습니다. 상세 결과는 [IMPORT_VALIDATION.md](docs/IMPORT_VALIDATION.md)를 참고하세요.

- GMA 변형의 기존 테스트 기대값과 실제 구현 결과가 불일치하며, 원본에서도 같은 실패가 재현됩니다.
- payload 검사기의 기존 필드 후보 경고 37건이 남아 있습니다. 모든 차트의 시각·의미 검증 완료를 뜻하지 않습니다.
- 지연·부분 라벨의 예측 매칭, 확보율 관리와 후행 재집계 전용 서버는 제공하지 않습니다.
- 모델 자동 배포·캐너리 제어·원인 자동 확정이 모두 구현된 운영 플랫폼을 의미하지 않습니다.
- LLM 해석 요청 시 제공한 차트 근거가 설정된 endpoint로 전송됩니다. 데이터의 전송 범위와 대상은 운영 환경에서 결정해야 합니다.

## 관련 문서

| 문서 | 내용 |
| --- | --- |
| [배포 설명](docs/DEPLOYMENT.md) | 저장소·접속 경계와 기존 LLM 테이블 초기화 |
| [최초 등록 검증 기록](docs/IMPORT_VALIDATION.md) | 실행한 검사·제외 범위·알려진 문제 |
| [서버 실행 구조](drift_control_plane/server_runtime_topology.md) | 서버별 책임·호출 경계 |
| [알고리즘 카탈로그](drift_algorithm_impl/drift_methods_catalog.md) | 방법·입력·출력·분류 |
| [Chart Runtime](chart_runtime/README.md) | payload·컴포넌트·렌더링 |
| [Chart Builder](chart_builder/README.md) | 차트 설계와 미리보기 |
| [LLM 해석 서버](llm_interpretation_server/README.md) | 근거 기반 설명과 API |

## 기여와 변경 규칙

변경 전 [개발 가이드](CODEX_DEVELOPMENT_GUIDE.md)와 [managed contract 목록](drift_control_plane/managed_contracts.csv)을 확인합니다. P0 항목 변경과 입출력 구조에 영향을 주는 P1 변경에는 사전 동의가 필요합니다. 관련 테스트와 계약 영향을 기록하고 `logs/`에 작업 로그를 남깁니다.

## 라이선스

[Apache License 2.0](LICENSE)을 따릅니다. 외부 라이브러리·모델·데이터에는 각각의 라이선스와 이용 조건이 적용됩니다.

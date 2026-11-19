# Sprint 17 V2 Matrix Contract

## 1. 목적

V2 matrix는 dataset, adapter, drift method, analysis chart, payload adapter 조합을 명시적으로 표현한다.

V1 Harness scenario는 하나의 완성된 E2E 입력이다. V2 matrix row는 scenario를 생성하거나 선택하기 위한 더 상위 입력이다.

## 2. Matrix Row Schema

```json
{
  "matrixRowId": "V2-ROW-CASE010-ADWIN-STREAM001",
  "status": "executable",
  "dataset": {
    "datasetCaseId": "CASE-010",
    "sourceId": "case-010",
    "csvPath": "테스트데이터/CASE-010_stream_numeric_mean_shift/data.csv",
    "signalType": "time_series_numeric"
  },
  "adapter": {
    "adapterType": "test_db_numeric_stream",
    "aggregateIntervalMinutes": 10,
    "bucketResolution": "10m"
  },
  "method": {
    "methodVariantKey": "ADWIN_MEAN_STREAM",
    "runtimeMethodKey": "adwin_mean_stream",
    "methodVariantId": 123,
    "algorithmImplementationId": 45
  },
  "chart": {
    "chartId": "CHART-STREAM-001",
    "analysisChartId": "analysis-case010-adwin-stream",
    "payloadAdapterKey": "adwin_mean_stream_to_chart_stream_001"
  },
  "harness": {
    "scenarioPath": "testing/harness/scenarios/case010_mode_a.json",
    "modes": ["A", "B"],
    "requiredValidations": ["timeseries", "event_analysis", "ui_state"]
  }
}
```

## 3. Required Fields

| Field | Required | 설명 |
| --- | --- | --- |
| `matrixRowId` | yes | matrix row stable id |
| `status` | yes | `executable`, `candidate_gap`, `blocked` |
| `dataset.datasetCaseId` | yes | 대표 dataset case id |
| `dataset.sourceId` | executable yes | Drift Server source id |
| `dataset.csvPath` | executable yes | Test Feeder 입력 CSV |
| `adapter.adapterType` | yes | source adapter type |
| `method.methodVariantKey` | yes | method catalog variant key |
| `method.runtimeMethodKey` | executable yes | Drift Server runtime registry key |
| `chart.chartId` | yes | chart runtime payload id |
| `chart.payloadAdapterKey` | executable yes | event context -> chart payload adapter key |
| `harness.scenarioPath` | executable yes | 기존 scenario 재사용 또는 생성 경로 |
| `harness.modes` | executable yes | 실행할 Mode A/B |

## 4. Status Semantics

```text
executable:
  runtimeMethodKey가 runtime registry에 있고 scenarioPath가 존재한다.
  Harness가 바로 실행할 수 있다.

candidate_gap:
  dataset/method/chart catalog에는 있지만 runtime wrapper나 scenario가 아직 없다.
  payload binding coverage만 통과했을 수 있다.

blocked:
  chart template, payload adapter, dataset, method contract 중 하나 이상이 없다.
```

## 5. Compatibility Rules

V2 compatibility는 세 층으로 나눈다.

```text
catalog compatible:
  chart_method_dataset_mapping.csv에 연결이 있다.

payload compatible:
  payload_adapter_coverage_report.json에서 binding이 passed다.

runtime executable:
  runtimeMethodKey가 Drift Server runtime registry에 있고 Harness scenario가 있다.
```

Sprint 17 기준으로 188개 pair는 payload compatible이다. 그러나 runtime executable은 ADWIN stream 중심 row만 해당한다.

## 6. Harness Matrix Runner 요구

Sprint 18의 matrix runner는 다음 입력을 받을 수 있어야 한다.

```text
matrix seed JSON path
status filter: executable only / include candidate
mode filter: A / B / both
row id filter
```

출력 artifact는 다음 구조를 목표로 한다.

```text
testing/runs/matrix/
  {matrix_run_id}/
    matrix_manifest.json
    row_results.json
    coverage_summary.json
    rows/
      {matrixRowId}/
        run_manifest.json
        validation_report.json
        summary.md
```

## 7. PyQt6 UI 영향

Sprint 16 UI는 단일 scenario 실행과 기존 artifact 조회를 지원한다.

Sprint 18 이후 matrix runner가 생기면 UI에는 다음 기능이 필요하다.

```text
matrix seed 선택
row status filter
matrix run 실행
row별 passed/failed summary
row artifact 열기
```


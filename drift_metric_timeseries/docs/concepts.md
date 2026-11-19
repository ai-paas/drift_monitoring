# 드리프트 지표 시계열 핵심 개념

작성일: 2026-06-24

이 문서는 `drift_metric_timeseries` 구현에서 사용하는 핵심 용어를 정리한다.

## 1. 상태 영역

| 개념 | 의미 |
|---|---|
| `Feature Registry` | 표시 가능한 feature 목록과 label/unit/missing policy 같은 메타데이터 영역 |
| `Time State` | 현재 시간 범위, 스케일, tick, display bucket 등 모든 panel이 공유하는 시간 상태 |
| `Feature Data Store` | feature별 시계열 bucket, drift event, loading/error/empty 상태 저장 영역 |
| `View / Render State` | primary/comparison feature, panel order, hover, popup, 결측 표시 옵션 같은 UI 상태 |

## 2. Feature 개념

| 개념 | 의미 |
|---|---|
| `Feature` | 드리프트를 측정하는 대상 값 |
| `Primary Feature` | 사용자가 기본으로 보는 기준 feature |
| `Comparison Feature` | primary feature와 같은 시간축으로 비교하는 추가 feature |
| `Feature Metadata` | feature의 label, unit, description, default y-scale, missing policy |
| `Feature Missing Policy` | 해당 feature에서 결측/휴무/보간 bucket을 어떻게 해석할지에 대한 정책 |
| `Panel Order` | 화면에 표시되는 feature panel 순서 |

예:

```text
embedding_distance
token_length
refusal_rate
latency_ms
```

## 3. 시간 개념

| 개념 | 의미 |
|---|---|
| `Full Domain` | 서버/데이터가 가진 전체 시간 범위 |
| `Visible Domain` | 현재 화면에 보이는 시간 범위 |
| `Range Preset` | 24H, 7D, 30D, 1Y, ALL 같은 빠른 범위 선택 |
| `Time Scale` | x축을 auto/hour/day/month/year 중 어떤 단위로 읽을지 |
| `Source Resolution` | 서버나 캐시에서 가져온 데이터 해상도 |
| `Display Bucket` | 화면에 표시하기 위해 사용하는 집계 단위 |
| `Tick Interval` | x축 tick 간격 |
| `Label Format` | x축 라벨 날짜/시간 형식 |
| `Navigator Selection` | 전체 기간 미니맵에서 선택된 현재 시간 구간 |

중요한 구분:

```text
Source Resolution = 서버/캐시 데이터 해상도
Display Bucket = 화면 표시용 집계 단위
Time Scale = 사용자가 x축을 읽는 단위
```

## 4. 데이터 개념

| 개념 | 의미 |
|---|---|
| `Feature Bucket` | 특정 feature의 특정 시간 구간 집계 row |
| `Bucket Start` | bucket 시작 시각 |
| `Bucket End` | bucket 종료 시각 |
| `Value / Mean` | 그래프에 표시할 대표값 |
| `Count` | bucket 안 원본 샘플 수 |
| `Resolution` | bucket의 집계 해상도 |
| `Y Domain` | feature panel의 y축 값 범위 |
| `Loaded Domain` | 현재 data store가 보유한 데이터 시간 범위 |
| `Data Request Key` | 시간 범위/feature/resolution 기준 cache 또는 요청 식별자 |
| `Loading / Loaded / Error / Empty` | feature별 데이터 로딩 상태 |

## 5. 결측과 품질 개념

| 개념 | 의미 |
|---|---|
| `Bucket Status` | bucket의 데이터 품질 상태 |
| `Observed` | 실제 관측 데이터가 있는 bucket |
| `Missing` | 기대했지만 데이터가 없는 bucket |
| `Closed` | 주말, 휴무, 라인 정지 등 원래 데이터가 없어도 되는 bucket |
| `Imputed` | 서버가 보간하거나 대체한 bucket |
| `Partial` | 일부 데이터만 들어온 불완전 bucket |
| `Coverage` | 기대 bucket 중 사용 가능한 bucket 비율 |
| `Expected Buckets` | 현재 범위에서 데이터가 기대되는 bucket 수 |
| `Observed Buckets` | 실제 관측 bucket 수 |
| `Missing Buckets` | 기대했지만 없는 bucket 수 |
| `Closed Buckets` | 비운영 bucket 수 |
| `Imputed Buckets` | 보간 bucket 수 |
| `Partial Buckets` | 일부 관측 bucket 수 |
| `Gap Count` | missing segment 개수 |
| `Gap Segment` | 연속된 missing 구간 |
| `Calendar Mode` | continuous/business 등 기대 bucket 계산 방식 |

기본 정책:

```text
UI는 missing을 0이나 주변값으로 임의 보간하지 않는다.
closed는 기본 coverage denominator에서 제외한다.
imputed는 값은 표시하되 실제 관측값과 구분한다.
partial은 coverage가 낮은 bucket으로 표시한다.
```

## 6. Drift 이벤트 개념

| 개념 | 의미 |
|---|---|
| `Drift Event` | 서버가 탐지한 warning/drift 시점 또는 구간 |
| `Warning` | 약한 드리프트 신호 |
| `Drift` | 확정 또는 강한 드리프트 |
| `Event Start` | 이벤트 시작 시각 |
| `Event End` | 이벤트 종료 시각 |
| `Event Score` | 이벤트 강도 또는 신뢰도 |
| `Event Label` | 이벤트 설명 |
| `Point Event` | 특정 시점 이벤트 |
| `Interval Event` | 일정 기간 지속된 이벤트 |

## 7. 렌더링 개념

| 개념 | 의미 |
|---|---|
| `Feature Panel` | feature 하나를 그리는 그래프 영역 |
| `Feature Panel Stack` | 여러 feature panel을 위아래로 쌓은 구조 |
| `Shared X-Axis` | 모든 feature panel이 공유하는 시간축 |
| `Independent Y-Axis` | feature별로 독립 계산하는 y축 |
| `Derived Render Model` | 상태와 데이터를 렌더링 가능한 형태로 변환한 결과 |
| `Panel Render Model` | feature panel 하나의 렌더링 데이터 |
| `Line Segment` | 연속 관측 구간을 잇는 선 |
| `Missing Segment` | 결측으로 선이 끊기는 구간 |
| `Closed Segment` | 비운영 구간 |
| `Imputed Segment` | 보간값이 포함된 구간 |
| `Hover Guide` | 같은 timestamp를 모든 panel에 표시하는 guide line |
| `Tooltip` | bucket/event 상세 정보 표시 |
| `Expanded Popup` | 같은 상태를 더 큰 영역에서 보는 확대 화면 |

## 8. 동기화 개념

| 개념 | 의미 |
|---|---|
| `Action` | 사용자 조작이나 데이터 이벤트를 표현하는 명령 |
| `Reducer` | action을 받아 상태를 변경하는 함수 |
| `Normalizer` | 상태 변경 후 불일치나 파생값을 정리하는 함수 |
| `State Synchronization` | 한 영역의 변경이 관련 영역과 render model에 반영되는 과정 |
| `Derived State` | 원본 상태에서 계산되는 tick, label, coverage, render model 등 |
| `Invariant` | 항상 지켜야 하는 상태 조건 |
| `Clamp` | visible domain이 full domain 밖으로 나가지 않게 제한하는 처리 |
| `Feature Validation` | 선택된 feature가 registry에 존재하는지 확인하는 처리 |
| `Coverage Recalculation` | 시간 범위/데이터 변경 후 coverage를 다시 계산하는 처리 |
| `Render Model Rebuild` | 상태와 데이터 변경 후 렌더링 모델을 다시 만드는 처리 |

대표 동기화 규칙:

```text
Time State 변경 -> 모든 표시 panel의 x축과 coverage/gap 재계산
View State 변경 -> 표시 feature 목록과 panel 배치 변경
Feature Data Store 변경 -> 해당 feature panel의 line/event/quality 갱신
Feature Registry 변경 -> selector와 metadata, feature 유효성 갱신
```

## 9. UI 조작 개념

| 개념 | 의미 |
|---|---|
| `Feature Selector` | primary feature 선택 UI |
| `Comparison Feature Add / Remove` | 비교 feature 추가/제거 UI |
| `Quick Range Preset` | 빠른 시간 범위 선택 |
| `Date/Time Range Picker` | 시작/종료 날짜와 시간 직접 선택 |
| `Pan` | 현재 범위 길이를 유지하며 시간 이동 |
| `Zoom` | 현재 범위를 좁히거나 넓히는 조작 |
| `Previous / Next Range` | 현재 구간 단위로 이전/다음 이동 |
| `Fit All` | 전체 기간 보기 |
| `Scale Selector` | auto/hour/day/month/year 선택 |
| `Navigator / Overview` | 전체 시간 범위 안의 현재 위치 표시 |
| `Hover Timestamp` | 현재 hover 중인 timestamp |
| `Popup Open / Close` | 확대 화면 열기/닫기 |

## 10. 테스트 개념

| 개념 | 의미 |
|---|---|
| `Harness` | 실제 차트 UI 없이 상태와 동기화를 검증하는 테스트 화면 |
| `Yearly Test Data` | 연단위 범위를 가진 synthetic bucket 데이터 |
| `Synthetic Drift Event` | 테스트용 warning/drift 이벤트 |
| `Action Sequence Test` | 여러 action을 연속 실행해 상태가 유지되는지 확인 |
| `Invariant Test` | 공유 x축, feature 중복 제거, domain clamp 같은 조건 검증 |
| `Missing Data Test` | missing/closed/imputed/partial 처리 검증 |
| `Coverage Test` | coverage와 bucket status count 계산 검증 |
| `Shared Axis Test` | 모든 panel의 xDomain/tick/displayBucket 일치 검증 |
| `Feature Status Test` | feature별 loading/error가 독립적으로 처리되는지 검증 |

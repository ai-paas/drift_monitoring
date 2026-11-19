# 드리프트 지표 시계열 시간 상태 모델

작성일: 2026-06-24

## 1. 목적

`drift_metric_timeseries`는 시간 이동, 범위 조정, 스케일 변경, 확대/축소, navigator 조작이 조합된다.
또한 하나의 primary feature를 보다가 comparison feature를 추가해 같은 시간축에서 여러 feature를 비교할 수 있다.

이 조작을 각 버튼이나 UI 요소에서 따로 처리하면 다음 문제가 생긴다.

```text
현재 보고 있는 범위와 x축 라벨이 불일치한다.
스케일은 월 단위인데 데이터는 시간 단위로 과도하게 표시된다.
사용자가 직접 선택한 범위가 preset 클릭으로 예상 밖으로 사라진다.
pan 이후 display bucket이나 tick interval이 갱신되지 않는다.
비교 feature를 추가했는데 기존 feature와 시간축이 어긋난다.
```

따라서 모든 시간 조작은 하나의 시간 상태를 변경하고, 렌더러는 정규화된 상태에서 파생된 값만 사용한다.
다중 feature 비교에서도 time state는 하나만 존재해야 하며, feature panel은 같은 time state를 공유한다.

## 2. 외부 컴포넌트 참고 패턴

대표 차트/피커 컴포넌트들은 시간 탐색을 여러 역할로 나눈다.

```text
Highcharts Stock Range Selector: 빠른 범위 버튼 + 시작/종료 입력
Highcharts Navigator: 전체 기간 미니맵과 현재 선택 구간
Highcharts Data Grouping: 화면 폭과 범위에 맞는 데이터 집계
Plotly Range Slider/Selector: 하단 슬라이더와 preset selector
ECharts dataZoom: 긴 시간축에서 일부 구간만 표시
TradingView Lightweight Charts Time Scale: visible range와 logical range 분리
MUI/React Aria DateRangePicker: 달력/시간 입력과 직접 범위 선택
```

관련 문서:

- https://www.highcharts.com/docs/stock/range-selector
- https://www.highcharts.com/docs/stock/navigator
- https://www.highcharts.com/docs/stock/data-grouping
- https://plotly.com/python/range-slider/
- https://echarts.apache.org/handbook/en/concepts/axis/
- https://tradingview.github.io/lightweight-charts/docs/time-scale
- https://mui.com/x/react-date-pickers/date-range-picker/
- https://react-aria.adobe.com/DateRangePicker

## 3. 상태 구조

구현 상태는 4개 영역으로 나눈다.

```text
Feature Registry: 무엇을 볼 수 있는가
Time State: 언제/어떤 스케일로 보는가
Feature Data Store: 실제 값과 drift 이벤트는 무엇인가
View / Render State: 화면에 무엇을 어떻게 배치하는가
```

이 4개 영역을 분리해야 시간 조작, feature 추가, 데이터 로딩, 화면 배치가 서로 섞이지 않는다.

### 3.1 Feature Registry

Feature Registry는 표시 가능한 feature 목록과 메타데이터를 가진다.

예:

```json
{
  "features": {
    "embedding_distance": {
      "label": "임베딩 거리",
      "unit": "distance",
      "description": "Reference와 current embedding 분포 거리",
      "defaultYScale": "auto",
      "missingPolicy": {
        "calendarMode": "business",
        "showClosed": false,
        "allowImputed": true
      }
    },
    "token_length": {
      "label": "토큰 길이",
      "unit": "tokens",
      "defaultYScale": "auto"
    }
  }
}
```

역할:

```text
feature selector 후보를 제공한다.
feature별 label/unit/기본 y축 정책을 제공한다.
feature별 missing policy와 calendar mode를 제공한다.
primary/comparison feature가 유효한지 검증한다.
```

### 3.2 Time State

Time State는 현재 보고 있는 시간 범위와 x축 표시 정책을 가진다.

권장 상태:

```json
{
  "fullDomain": ["2021-01-01T00:00:00Z", "2026-06-24T00:00:00Z"],
  "visibleDomain": ["2026-06-01T09:00:00Z", "2026-06-08T18:00:00Z"],
  "rangePreset": "CUSTOM",
  "scaleMode": "hour",
  "bucketMode": "auto",
  "manualBucket": null,
  "displayBucket": "1h",
  "sourceResolution": "1h",
  "tickInterval": "12h",
  "labelFormat": "MM-dd HH:00",
  "navigatorSelection": ["2026-06-01T09:00:00Z", "2026-06-08T18:00:00Z"],
  "dataRequestKey": "2026-06-01T09:00:00Z..2026-06-08T18:00:00Z|1h"
}
```

필드 의미:

| field | 의미 |
|---|---|
| `fullDomain` | 서버/캐시가 알고 있는 전체 데이터 시간 범위 |
| `visibleDomain` | 현재 메인 그래프가 표시하는 시작/종료 시각 |
| `rangePreset` | `1D`, `7D`, `1M`, `ALL`, `CUSTOM` 등 현재 범위 선택 방식 |
| `scaleMode` | `auto`, `hour`, `day`, `month`, `year` 중 x축 읽기 단위 |
| `bucketMode` | `auto` 또는 `manual` |
| `manualBucket` | 사용자가 직접 선택한 집계 단위 |
| `displayBucket` | 실제 렌더링에 사용할 집계 단위 |
| `sourceResolution` | 서버/캐시에서 가져올 원천 집계 해상도 |
| `tickInterval` | x축 tick 간격 |
| `labelFormat` | x축 라벨 포맷 |
| `navigatorSelection` | 전체 기간 미니맵의 선택 구간 |
| `dataRequestKey` | 현재 시간 범위와 해상도 기준 요청/캐시 판별 키 |

주의:

```text
primaryFeature와 comparisonFeatures는 아래 View / Render State에만 둔다.
Time State 자체에는 feature 목록을 넣지 않는다.
```

### 3.3 Feature Data Store

Feature Data Store는 feature별 series bucket, drift event, 로딩 상태를 가진다.

```json
{
  "featureData": {
    "embedding_distance": {
      "series": [],
      "events": [],
      "sourceResolution": "1h",
      "loadedDomain": ["2026-06-01T00:00:00Z", "2026-06-09T00:00:00Z"],
      "status": "loaded",
      "error": null,
      "coverageSummary": {
        "expected": 168,
        "observed": 150,
        "missing": 8,
        "closed": 6,
        "imputed": 3,
        "partial": 1
      }
    },
    "token_length": {
      "series": [],
      "events": [],
      "sourceResolution": "1h",
      "loadedDomain": null,
      "status": "loading",
      "error": null
    }
  }
}
```

역할:

```text
feature별 시계열 데이터를 저장한다.
feature별 warning/drift 이벤트를 저장한다.
bucket별 observed/missing/closed/imputed/partial 상태를 저장한다.
feature별 loading/empty/error 상태를 저장한다.
현재 Time State에 필요한 데이터가 캐시에 있는지 판단한다.
```

### 3.4 View / Render State

View / Render State는 화면 배치와 사용자 선택 상태를 가진다.

```json
{
  "viewState": {
    "primaryFeature": "embedding_distance",
    "comparisonFeatures": ["token_length", "refusal_rate"],
    "panelOrder": ["embedding_distance", "token_length", "refusal_rate"],
    "hoverTimestamp": "2026-06-04T12:00:00Z",
    "expanded": false,
    "popupOpen": false,
    "missingDisplay": {
      "showMissingBands": true,
      "showClosedBands": false,
      "showImputedStyle": true,
      "showCoverageSummary": true
    }
  }
}
```

역할:

```text
어떤 feature panel을 표시할지 결정한다.
panel 순서와 layout을 결정한다.
hover 동기화 상태를 가진다.
확대 popup 상태를 가진다.
결측/비운영/보간 구간 표시 옵션을 가진다.
```

### 3.5 분리 원칙

```text
Feature Registry는 feature metadata만 가진다.
Time State는 feature 목록을 모르고, 시간 범위와 x축 정책만 가진다.
Feature Data Store는 데이터와 이벤트를 feature별로 가진다.
View / Render State는 표시 중인 feature와 UI 상태를 가진다.
```

간단히 말하면:

```text
Feature Registry = 무엇을 볼 수 있는가
Time State = 언제/어떤 스케일로 보는가
Feature Data Store = 실제 값과 이벤트는 무엇인가
View / Render State = 화면에 무엇을 어떻게 배치하는가
```

## 3.6 영역 간 영향 관계

한 영역의 변경은 다른 영역에 아래처럼 영향을 준다.

| 변경 영역 | 직접 영향 | 직접 바꾸지 않는 것 |
|---|---|---|
| Feature Registry | feature selector 후보, label/unit, feature 유효성 | Time State, raw data |
| Time State | 모든 표시 feature panel의 x축, 데이터 필요 범위, tick/label, navigator, expected bucket 계산 | primary/comparison feature 선택 |
| Feature Data Store | panel별 line/event/loading/error/coverage/gap 렌더링 | visibleDomain, scaleMode, panel order |
| View / Render State | 표시할 feature 목록, panel 배치, hover/popup, 결측 표시 옵션 | source data, fullDomain |

### Feature Registry 변경

Feature Registry가 바뀌는 경우:

```text
새 feature metadata 로드
feature label/unit 변경
feature 목록 갱신
feature missingPolicy 변경
```

영향:

```text
feature selector 후보를 다시 만든다.
View State의 primary/comparison feature가 더 이상 유효하지 않으면 제거하거나 fallback feature를 선택한다.
missingPolicy가 바뀌면 coverage/gap 계산 방식을 다시 적용한다.
Feature Data Store는 필요한 feature 데이터만 유지하거나 stale 처리할 수 있다.
Time State는 변경하지 않는다.
```

### Time State 변경

Time State가 바뀌는 경우:

```text
range preset 선택
직접 날짜/시간 선택
pan/zoom
scale 변경
navigator brush
plot resize에 따른 tick 재계산
```

영향:

```text
모든 표시 feature panel의 x축을 같은 visibleDomain으로 다시 계산한다.
tickInterval과 labelFormat을 다시 계산한다.
expected bucket과 coverage/gap을 다시 계산한다.
Feature Data Store에 현재 visibleDomain/sourceResolution 데이터가 있는지 확인한다.
부족한 데이터가 있으면 표시 중인 feature별로 요청한다.
View State의 primary/comparison feature 목록은 유지한다.
Feature Registry는 변경하지 않는다.
```

### Feature Data Store 변경

Feature Data Store가 바뀌는 경우:

```text
feature 데이터 로딩 완료
feature 이벤트 로딩 완료
feature 데이터 요청 실패
bucket status 변경
cache 갱신
```

영향:

```text
해당 feature panel만 line/band/event/loading/error 표시를 갱신한다.
필요하면 feature별 yDomain을 다시 계산한다.
해당 feature panel의 coverage/gap/segment를 다시 계산한다.
같은 Time State를 쓰는 다른 panel의 x축은 변경하지 않는다.
Time State와 View State는 원칙적으로 변경하지 않는다.
```

### View / Render State 변경

View / Render State가 바뀌는 경우:

```text
primary feature 변경
comparison feature 추가/제거
panel 순서 변경
hover timestamp 변경
확대 popup 열기/닫기
결측 표시 옵션 변경
```

영향:

```text
표시할 feature panel 목록을 다시 만든다.
새로 표시된 feature에 필요한 데이터가 Feature Data Store에 없으면 현재 Time State 기준으로 요청한다.
hoverTimestamp가 바뀌면 모든 표시 panel에 같은 vertical guide를 표시한다.
결측 표시 옵션이 바뀌면 data 자체는 유지하고 render segment 표시만 바꾼다.
확대 popup이 열리면 plot size 기준으로 tick/displayBucket을 재계산할 수 있다.
Time State의 visibleDomain은 변경하지 않는다.
Feature Registry는 변경하지 않는다.
```

확대 popup은 예외적으로 plot width/height가 바뀌므로 Time State의 derived 값인 `tickInterval`, `labelFormat`, `displayBucket` 재계산을 유발할 수 있다. 하지만 사용자가 보던 `visibleDomain` 자체는 유지한다.

## 3.7 Bucket Status와 Coverage

bucket은 값뿐 아니라 데이터 품질 상태를 가진다.

```json
{
  "bucket_start": "2026-06-04T12:00:00Z",
  "bucket_end": "2026-06-04T13:00:00Z",
  "mean": null,
  "count": 0,
  "status": "missing",
  "coverage": 0
}
```

status:

| status | 의미 | 렌더링 원칙 |
|---|---|---|
| `observed` | 실제 관측 데이터 있음 | 정상 line/point |
| `missing` | 기대했지만 데이터 없음 | line을 끊고 결측 segment 표시 |
| `closed` | 비운영 시간 | coverage 계산에서 제외 가능, 연한 band |
| `imputed` | 서버 보간값 | 값은 표시하되 점선/별도 marker |
| `partial` | 일부 관측 | 값은 표시하되 낮은 coverage 표시 |

coverage 계산:

```text
expectedBuckets = observed + missing + imputed + partial
closed는 기본 coverage denominator에서 제외한다.
coverage = (observed + imputed + partial) / expectedBuckets
```

주의:

```text
UI는 missing을 0이나 주변값으로 임의 보간하지 않는다.
서버가 보간한 값은 status=imputed로 명시되어야 한다.
결측 구간은 drift 해석에 영향을 주므로 화면에서 숨기지 않는다.
```

render model은 다음 값을 가져야 한다.

```json
{
  "expectedBuckets": 120,
  "observedBuckets": 98,
  "missingBuckets": 12,
  "closedBuckets": 10,
  "imputedBuckets": 6,
  "partialBuckets": 4,
  "coverage": 0.9,
  "gapCount": 3,
  "segments": [
    {"type": "observed", "from": "...", "to": "..."},
    {"type": "missing", "from": "...", "to": "..."},
    {"type": "observed", "from": "...", "to": "..."}
  ]
}
```

## 4. 사용자 액션

모든 UI 조작은 아래 액션 중 하나로 변환한다.

| action | 발생 UI |
|---|---|
| `INIT` | 컴포넌트 초기화 |
| `SET_RANGE_PRESET` | 오늘, 최근 7일, 1개월, 전체 등 빠른 범위 버튼 |
| `SET_VISIBLE_DOMAIN` | 날짜/시간 직접 입력 후 적용 |
| `BRUSH_RANGE` | navigator에서 구간 드래그 |
| `PAN_BY_DELTA` | 이전/다음 구간 버튼, drag pan |
| `ZOOM_AT` | wheel/pinch zoom, plot 영역 drag zoom |
| `SET_SCALE_MODE` | 자동/시간/일/월/연 스케일 선택 |
| `SET_PRIMARY_FEATURE` | 기준 feature 변경 |
| `ADD_COMPARISON_FEATURE` | 비교 feature 추가 |
| `REMOVE_COMPARISON_FEATURE` | 비교 feature 제거 |
| `SET_BUCKET_MODE` | 자동/수동 집계 전환 |
| `SET_MANUAL_BUCKET` | 수동 집계 단위 선택 |
| `FIT_ALL` | 전체 보기 |
| `JUMP_TO_TIME` | 특정 이벤트나 날짜로 이동 |
| `DATA_LOADED` | 서버/캐시 데이터 수신 |
| `RESIZE_PLOT` | 컴포넌트 폭 변경 또는 확대 popup 표시 |

## 5. 정규화 파이프라인

액션이 들어오면 다음 순서로 상태를 다시 계산한다.

```text
1. visibleDomain 결정
2. visibleDomain을 fullDomain 안으로 clamp
3. rangePreset과 CUSTOM 여부 결정
4. scaleMode 확인
5. bucketMode/manualBucket 확인
6. visibleDomain + scaleMode + plot width로 displayBucket 결정
7. 필요한 sourceResolution 결정
8. data cache hit/miss 확인
9. tickInterval 결정
10. labelFormat 결정
11. label collision 검사
12. navigatorSelection 동기화
13. 표시 feature 목록 확인
14. feature별 data cache hit/miss 확인
15. feature별 yDomain/threshold/event 정규화
16. render payload 생성
```

중요한 점:

```text
UI 버튼은 축, 라벨, 데이터, 미니맵을 직접 고치지 않는다.
UI 버튼은 action만 발생시킨다.
렌더링은 항상 정규화된 상태에서 파생한다.
feature 추가/제거는 time state를 변경하지 않는다.
time state 변경은 모든 표시 feature panel에 동시에 적용한다.
```

## 6. 불변 조건

렌더러는 항상 아래 조건을 만족해야 한다.

```text
visibleDomain.start < visibleDomain.end
visibleDomain은 fullDomain 안에 있어야 한다.
displayBucket은 visibleDomain과 plot width에 비해 과도하게 촘촘하면 안 된다.
tickInterval은 x축 라벨이 겹치지 않는 수준이어야 한다.
sourceResolution은 displayBucket보다 같거나 더 세밀한 해상도여야 한다.
manualBucket이 현재 범위에 부적합하면 경고 후 auto fallback을 허용한다.
navigatorSelection은 visibleDomain과 동기화되어야 한다.
모든 feature panel은 동일한 visibleDomain/tickInterval/labelFormat을 사용해야 한다.
feature별 yDomain은 독립적으로 계산한다.
서로 단위가 다른 feature를 하나의 y축에 강제로 공유하면 안 된다.
```

## 7. 조작 예시

이전 구간 이동:

```text
현재: 2026-06-01 09:00 ~ 2026-06-08 18:00
액션: PAN_BY_DELTA(-rangeLength)
결과: 2026-05-24 00:00 ~ 2026-06-01 09:00
스케일: 기존 hour 유지 가능 여부 확인
tick/display bucket 재계산
```

최근 30일 선택:

```text
액션: SET_RANGE_PRESET("30D")
visibleDomain: now - 30d ~ now
rangePreset: "30D"
scaleMode: auto면 day 또는 week 후보
displayBucket: 1d 후보
```

직접 날짜/시간 선택:

```text
액션: SET_VISIBLE_DOMAIN("2026-06-01T09:00:00Z", "2026-06-08T18:00:00Z")
rangePreset: CUSTOM
scaleMode: 기존 선택 유지 또는 auto
displayBucket/tick/label 재계산
```

범위를 좁힌 뒤 시간 스케일 선택:

```text
액션 1: SET_VISIBLE_DOMAIN("2026-06-24T00:00:00Z", "2026-06-24T23:00:00Z")
액션 2: SET_SCALE_MODE("hour")
결과: visibleDomain은 유지, x축 라벨과 displayBucket만 시간 단위에 맞게 재계산
```

월 단위 장기 범위에서 시간 스케일 선택:

```text
현재: 2024-01-01 ~ 2026-06-24
액션: SET_SCALE_MODE("hour")
처리: 너무 넓은 범위라면 hour scale 적용 불가 또는 visibleDomain 축소 제안
권장: 상태는 유지하고 사용자에게 "시간 단위 보기는 범위를 더 좁혀야 함"을 표시
```

비교 feature 추가:

```text
현재: primaryFeature = embedding_distance
현재 visibleDomain: 2026-06-01 09:00 ~ 2026-06-08 18:00
액션: ADD_COMPARISON_FEATURE("token_length")
결과: comparisonFeatures에 token_length 추가
time state: 변경 없음
데이터 요청: token_length + 현재 visibleDomain + 현재 sourceResolution
렌더링: token_length panel을 같은 x축으로 아래에 추가
```

primary feature 변경:

```text
액션: SET_PRIMARY_FEATURE("refusal_rate")
결과: primaryFeature 변경
time state: 변경 없음
comparison feature 목록은 유지하거나 중복 feature만 제거
렌더링: refusal_rate panel을 기준 panel로 표시
```

## 8. 데이터 요청과 캐시

서버는 가능하면 여러 집계 해상도를 제공한다.

```text
10m
1h
1d
1w
1M
```

UI는 현재 visibleDomain보다 약간 넓은 범위를 가져와 pan 시 재요청을 줄일 수 있다.

```text
requestDomain = visibleDomain + padding
padding = visible span의 0.5배 또는 설정값
```

요청 정책:

```text
캐시가 visibleDomain과 필요한 sourceResolution을 포함하면 서버 요청 없음
캐시가 일부 부족하면 부족한 구간만 요청
더 세밀한 sourceResolution이 필요하면 해당 해상도 요청
displayBucket 변경만으로 해결 가능하면 UI에서 재집계
```

다중 feature 요청 정책:

```text
같은 visibleDomain/sourceResolution으로 표시 feature를 요청한다.
서버가 batch feature 요청을 지원하면 한 번에 요청한다.
지원하지 않으면 feature별 요청을 병렬로 수행한다.
한 feature 요청 실패가 전체 컴포넌트 실패가 되면 안 된다.
실패한 feature panel만 error 상태로 표시한다.
```

서버 해상도와 표시 해상도는 분리한다.

```text
sourceResolution = 서버/캐시에서 받은 데이터 해상도
displayBucket = 화면에 그릴 때 사용하는 집계 단위
```

## 9. UI 표시 요구

시간 상태가 복잡하므로 다음 정보를 항상 사용자가 볼 수 있어야 한다.

```text
현재 범위: 2026-06-01 09:00 ~ 2026-06-08 18:00
범위 길이: 7일 9시간
축 스케일: 시간
집계 단위: 1시간 평균
전체 위치: navigator 안의 선택 영역
현재 범위 이벤트: warning 3건, drift 1건
표시 feature: 임베딩 거리 + 토큰 길이 + 거절률
```

권장 상태 요약:

```text
2026-06-01 09:00 ~ 2026-06-08 18:00 · 7일 9시간 · 시간 축 · 1시간 평균 · warning 3 / drift 1
```

## 10. 테스트 시나리오

필수 테스트:

```text
시간 이동 -> 범위 조정 -> 스케일 조정 -> 다시 시간 이동
빠른 범위 선택 -> 직접 날짜/시간 선택 -> 전체 보기
긴 범위에서 hour scale 선택
짧은 범위에서 month scale 선택
plot width 변경 후 tick label 재계산
확대 popup 진입 후 displayBucket/tick 재계산
캐시 범위 안 pan은 서버 요청 없음
캐시 범위 밖 pan은 부족 구간만 요청
dense data는 집계되어 과도한 point를 그리지 않음
comparison feature 추가 후 모든 panel의 x축이 동일함
primary feature 변경 후 visibleDomain이 유지됨
한 feature 데이터 실패 시 나머지 feature panel은 유지됨
feature별 y축 단위가 다를 때 y축을 공유하지 않음
```

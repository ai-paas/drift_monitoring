# 드리프트 지표 시계열 React 구현 설계

작성일: 2026-06-24

이 문서는 `drift_metric_timeseries`를 React로 구현할 때 주요 개념을 어떤 컴포넌트, 상태, reducer, hook으로 나눌지 정리한다.

관련 문서:

- [functional_requirements.md](./functional_requirements.md)
- [ui_requirements.md](./ui_requirements.md)
- [state_model.md](./state_model.md)
- [implementation_notes.md](./implementation_notes.md)

## 1. 구현 원칙

핵심 원칙:

```text
Time State는 하나만 둔다.
Feature Panel은 여러 개 둘 수 있다.
모든 Feature Panel은 같은 Time State를 props로 받는다.
Feature별 데이터, 이벤트, y축은 독립적으로 계산한다.
사용자 조작은 DOM을 직접 고치지 않고 action으로 reducer에 전달한다.
상태 변경 후 필요한 데이터 요청과 렌더링은 React 흐름에 맡긴다.
```

상태 영역:

```text
Feature Registry: useFeatureRegistry()
Time State: useReducer(timeReducer)
Feature Data Store: useFeatureSeries/useFeatureEvents 또는 query cache
View / Render State: useReducer(viewReducer) 또는 통합 reducer
```

## 2. 컴포넌트 구조

권장 구조:

```tsx
<DriftMetricTimeseries>
  <ChartToolbar />
  <TimeStateSummary />
  <FeaturePanelStack>
    <FeaturePanel />
    <FeaturePanel />
  </FeaturePanelStack>
  <TimeNavigator />
  <ExpandedChartDialog />
</DriftMetricTimeseries>
```

역할:

| component | 책임 |
|---|---|
| `DriftMetricTimeseries` | 최상위 coordinator, reducer 보유, data hook 연결 |
| `ChartToolbar` | feature 선택, 비교 feature 추가/제거, range/scale 조작 |
| `TimeStateSummary` | 현재 시간 범위, 스케일, 집계, 이벤트 개수 표시 |
| `FeaturePanelStack` | 표시 feature 목록을 stacked panel로 배치 |
| `FeaturePanel` | feature 하나의 line/band/event/y축 렌더링 |
| `SharedXAxis` | 공유 x축 tick/label 렌더링 |
| `TimeNavigator` | 전체 기간과 현재 visibleDomain 표시, brush 조작 |
| `ExpandedChartDialog` | 확대 popup, 같은 상태로 더 큰 plot 렌더링 |

## 3. 최상위 상태

최상위 컴포넌트는 최소한 두 상태를 가진다.

```ts
type DriftMetricState = {
  time: TimeState;
  view: ViewState;
};
```

`TimeState`:

```ts
type TimeScaleMode = "auto" | "hour" | "day" | "month" | "year";

type TimeState = {
  fullDomain: [Date, Date] | null;
  visibleDomain: [Date, Date] | null;
  rangePreset: "24H" | "7D" | "30D" | "3M" | "1Y" | "ALL" | "CUSTOM";
  scaleMode: TimeScaleMode;
  sourceResolution: "1h" | "1d" | "1w" | "1M";
  displayBucket: "auto" | "1h" | "1d" | "1w" | "1M";
  tickInterval: string;
  labelFormat: string;
};
```

`ViewState`:

```ts
type ViewState = {
  primaryFeature: string;
  comparisonFeatures: string[];
  panelOrder: string[];
  hoverTimestamp: Date | null;
  expanded: boolean;
};
```

`Feature Registry`:

```ts
type FeatureMeta = {
  featureId: string;
  label: string;
  unit?: string;
  description?: string;
  defaultYScale?: "auto" | [number, number];
  missingPolicy?: {
    calendarMode: "continuous" | "business";
    showClosed?: boolean;
    allowImputed?: boolean;
  };
};
```

`Feature Data`:

```ts
type FeatureBucket = {
  featureId: string;
  bucketStart: string;
  bucketEnd?: string;
  resolution?: string;
  count?: number;
  mean?: number;
  value?: number;
  min?: number;
  max?: number;
  status?: "observed" | "missing" | "closed" | "imputed" | "partial";
  coverage?: number;
};

type DriftEvent = {
  featureId: string;
  start: string;
  end?: string;
  level: "normal" | "warning" | "drift";
  score?: number;
  label?: string;
};
```

## 4. Action 설계

시간 조작 action:

```ts
type TimeAction =
  | { type: "SET_RANGE_PRESET"; preset: TimeState["rangePreset"] }
  | { type: "SET_VISIBLE_DOMAIN"; domain: [Date, Date] }
  | { type: "PAN_BY_DELTA"; deltaMs: number }
  | { type: "ZOOM_AT"; anchor: Date; factor: number }
  | { type: "SET_SCALE_MODE"; scaleMode: TimeScaleMode }
  | { type: "BRUSH_RANGE"; domain: [Date, Date] }
  | { type: "FIT_ALL" }
  | { type: "RESIZE_PLOT"; plotWidth: number };
```

화면 조작 action:

```ts
type ViewAction =
  | { type: "SET_PRIMARY_FEATURE"; featureId: string }
  | { type: "ADD_COMPARISON_FEATURE"; featureId: string }
  | { type: "REMOVE_COMPARISON_FEATURE"; featureId: string }
  | { type: "SET_HOVER_TIMESTAMP"; timestamp: Date | null }
  | { type: "SET_EXPANDED"; expanded: boolean };
```

통합 reducer를 쓰면 action 처리 후 `normalizeState`를 한 번 호출한다.

```ts
type Action = TimeAction | ViewAction;

function reducer(state: DriftMetricState, action: Action): DriftMetricState {
  const next = applyAction(state, action);
  return normalizeState(next);
}
```

## 5. 정규화 함수

`normalizeState`는 상태 간 불일치를 제거한다.

```ts
function normalizeState(state: DriftMetricState): DriftMetricState {
  return pipe(
    clampVisibleDomain,
    ensureValidFeatureSelection,
    resolveDisplayBucket,
    resolveTickInterval,
    resolveLabelFormat,
    syncPanelOrder
  )(state);
}
```

책임:

```text
visibleDomain이 fullDomain 밖으로 나가지 않게 한다.
primary/comparison feature 중복을 제거한다.
삭제된 feature가 선택되어 있으면 fallback을 고른다.
plot width와 visibleDomain 기준으로 tickInterval을 고른다.
scaleMode와 visibleDomain 기준으로 displayBucket을 고른다.
panelOrder가 표시 feature 목록과 일치하게 한다.
```

주의:

```text
normalizeState는 서버 데이터를 직접 요청하지 않는다.
normalizeState는 DOM을 직접 수정하지 않는다.
normalizeState는 다음 상태만 반환한다.
```

## 6. 데이터 Hook

Feature Registry:

```ts
function useFeatureRegistry(modelId: string): {
  features: FeatureMeta[];
  loading: boolean;
  error: Error | null;
};
```

표시 feature 목록:

```ts
function useVisibleFeatures(view: ViewState): string[] {
  return [view.primaryFeature, ...view.comparisonFeatures];
}
```

feature별 series:

```ts
function useFeatureSeries(params: {
  modelId: string;
  featureId: string;
  visibleDomain: [Date, Date] | null;
  sourceResolution: string;
}): {
  data: FeatureBucket[];
  loading: boolean;
  error: Error | null;
};
```

feature별 drift events:

```ts
function useFeatureEvents(params: {
  modelId: string;
  featureId: string;
  visibleDomain: [Date, Date] | null;
}): {
  events: DriftEvent[];
  loading: boolean;
  error: Error | null;
};
```

React Query 또는 SWR을 쓰는 경우 cache key:

```ts
["drift-series", modelId, featureId, from, to, sourceResolution]
["drift-events", modelId, featureId, from, to]
```

1차 구현은 custom hook + 간단한 in-memory cache로 시작할 수 있다. 여러 화면에서 공유되면 React Query/SWR을 고려한다.

## 7. 렌더링 데이터 생성

`FeaturePanel`은 원본 bucket을 직접 그리지 않고, 렌더링용 데이터로 변환한다.

```ts
type PanelRenderModel = {
  feature: FeatureMeta;
  points: Array<{ x: number; y: number; bucket: FeatureBucket }>;
  events: Array<{ x1: number; x2?: number; level: "warning" | "drift" }>;
  yDomain: [number, number];
  quality: {
    expectedBuckets: number;
    observedBuckets: number;
    missingBuckets: number;
    closedBuckets: number;
    imputedBuckets: number;
    partialBuckets: number;
    coverage: number;
    gapCount: number;
  };
  segments: Array<{
    type: "observed" | "missing" | "closed" | "imputed" | "partial";
    from: string;
    to: string;
  }>;
  loading: boolean;
  error: Error | null;
};
```

생성 함수:

```ts
function buildPanelRenderModel(params: {
  feature: FeatureMeta;
  series: FeatureBucket[];
  events: DriftEvent[];
  timeState: TimeState;
  plotSize: { width: number; height: number };
}): PanelRenderModel;
```

책임:

```text
visibleDomain 기준으로 series/events를 필터링한다.
displayBucket 기준으로 필요한 경우 UI 재집계한다.
bucket status 기준으로 observed/missing/closed/imputed/partial을 분리한다.
missing은 line segment를 끊고 gap으로 계산한다.
closed는 기본 coverage denominator에서 제외한다.
imputed/partial은 값은 사용할 수 있으나 실제 관측값과 구분한다.
xScale은 공유 Time State에서 만든다.
yScale은 feature별로 독립 계산한다.
warning/drift 이벤트를 marker 또는 band로 변환한다.
```

## 8. 화면 갱신 범위

상태 변경별 렌더링 영향:

| 변경 | 주 화면 영향 |
|---|---|
| `TimeState.visibleDomain` | 모든 panel x축/line/event/navigator/summary 갱신 |
| `TimeState.scaleMode` | tick/label/displayBucket과 모든 panel 갱신 |
| `ViewState.comparisonFeatures` | panel 추가/제거, 필요한 feature 데이터 hook 활성화 |
| `ViewState.hoverTimestamp` | vertical guide와 tooltip만 갱신 |
| feature series 로딩 완료 | 해당 feature panel line/band 갱신 |
| feature events 로딩 완료 | 해당 feature panel event 표시 갱신 |
| feature registry 갱신 | selector, label, unit, 유효성 검증 |

React 최적화:

```text
FeaturePanel은 React.memo를 적용할 수 있다.
buildPanelRenderModel은 useMemo로 계산한다.
hover guide는 가능하면 가벼운 overlay로 분리한다.
대량 point는 SVG path 하나로 렌더링한다.
point marker는 sparse 상태에서만 표시한다.
```

## 9. 컴포넌트 Props 초안

최상위:

```ts
type DriftMetricTimeseriesProps = {
  modelId: string;
  initialPrimaryFeature?: string;
  initialComparisonFeatures?: string[];
  initialVisibleDomain?: [Date, Date];
  initialScaleMode?: TimeScaleMode;
  dataProvider: DriftMetricDataProvider;
};
```

data provider:

```ts
type DriftMetricDataProvider = {
  listFeatures(modelId: string): Promise<FeatureMeta[]>;
  loadSeries(params: {
    modelId: string;
    featureId: string;
    from: Date;
    to: Date;
    sourceResolution: string;
  }): Promise<FeatureBucket[]>;
  loadEvents(params: {
    modelId: string;
    featureId: string;
    from: Date;
    to: Date;
  }): Promise<DriftEvent[]>;
};
```

이렇게 하면 서버 통신 방식이 바뀌어도 chart 컴포넌트 내부 구조는 유지할 수 있다.

## 10. 사용자 조작 흐름

비교 feature 추가:

```text
사용자 [+ 비교 feature] 선택
-> dispatch({ type: "ADD_COMPARISON_FEATURE", featureId })
-> viewState.comparisonFeatures 갱신
-> useVisibleFeatures 결과 변경
-> 해당 feature의 useFeatureSeries/useFeatureEvents 활성화
-> 로딩 중 panel 표시
-> 데이터 도착 후 같은 Time State로 렌더링
```

시간 범위 변경:

```text
사용자 7D preset 클릭
-> dispatch({ type: "SET_RANGE_PRESET", preset: "7D" })
-> timeState.visibleDomain 변경
-> tick/displayBucket 재계산
-> 모든 표시 feature hook의 cache key 변경
-> 필요한 데이터 로딩
-> 모든 panel이 같은 x축으로 렌더링
```

hover:

```text
FeaturePanel에서 pointer move
-> timestamp 계산
-> dispatch({ type: "SET_HOVER_TIMESTAMP", timestamp })
-> 모든 panel의 HoverGuide가 같은 timestamp 위치 표시
```

확대 popup:

```text
사용자 expand 클릭
-> dispatch({ type: "SET_EXPANDED", expanded: true })
-> ExpandedChartDialog 표시
-> 더 큰 plotSize 기준으로 tick/displayBucket 재계산 가능
-> visibleDomain은 유지
```

## 11. 초기 구현 순서

권장 순서:

```text
1. 타입 정의와 dataProvider interface 작성
2. time/view reducer와 normalizeState 작성
3. Feature Registry hook 작성
4. 단일 FeaturePanel 렌더링
5. Time toolbar와 상태 요약 연결
6. comparison feature 추가/제거
7. shared x-axis와 hover sync
8. navigator/overview
9. 확대 popup
10. 성능 최적화와 테스트
```

## 12. 테스트 포인트

필수 테스트:

```text
primary feature 하나만 표시된다.
comparison feature 추가 시 visibleDomain이 유지된다.
comparison feature 제거 시 Time State가 바뀌지 않는다.
range preset 변경 시 모든 panel의 x축이 동일하다.
scaleMode 변경 시 tick/label이 모든 panel에서 동일하다.
feature별 y축은 독립적으로 계산된다.
한 feature 로딩 실패가 다른 panel을 깨지 않는다.
hover timestamp가 모든 panel에 동기화된다.
확대 popup에서도 visibleDomain이 유지된다.
```

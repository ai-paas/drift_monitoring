# 드리프트 지표 시계열 구현 메모

작성일: 2026-06-24

이 문서는 요구사항 문서에서 제외한 구현 세부, 참고 패턴, 후순위 기능을 정리한다. 필수 요구사항은 [functional_requirements.md](./functional_requirements.md)와 [ui_requirements.md](./ui_requirements.md)를 우선한다.

## 1. 후순위 기능

1차 구현에서 제외하거나 옵션으로 둔다.

```text
event click
drilldown
legend toggle
multi-level x-axis label
panel 접기/펼치기
통합 tooltip에서 모든 feature 값 표시
jump_to_time
manualBucket 직접 선택
recovered 이벤트 level
p05/p95/stddev/last 상세 통계 표시
cache padding 세부 규칙
batch 요청/병렬 요청 최적화
```

## 2. 외부 컴포넌트 참고

대표 패턴:

```text
Highcharts Stock Range Selector: 빠른 범위 버튼 + 시작/종료 입력
Highcharts Navigator: 전체 기간 미니맵과 현재 선택 구간
Highcharts Data Grouping: 화면 폭과 범위에 맞는 데이터 집계
Plotly Range Slider/Selector: 하단 슬라이더와 preset selector
ECharts dataZoom: 긴 시간축에서 일부 구간만 표시
TradingView Lightweight Charts Time Scale: visible range와 logical range 분리
MUI/React Aria DateRangePicker: 달력/시간 입력
```

참고 링크:

- https://www.highcharts.com/docs/stock/range-selector
- https://www.highcharts.com/docs/stock/navigator
- https://www.highcharts.com/docs/stock/data-grouping
- https://plotly.com/python/range-slider/
- https://echarts.apache.org/handbook/en/concepts/axis/
- https://tradingview.github.io/lightweight-charts/docs/time-scale
- https://mui.com/x/react-date-pickers/date-range-picker/
- https://react-aria.adobe.com/DateRangePicker

## 3. 상세 입력 예시

집계 row 예:

```json
{
  "model_id": "model-a",
  "feature_id": "embedding_distance",
  "bucket_start": "2026-06-24T00:00:00Z",
  "bucket_end": "2026-06-24T01:00:00Z",
  "resolution": "1h",
  "count": 120,
  "mean": 0.42,
  "min": 0.31,
  "max": 0.55,
  "p05": 0.33,
  "p95": 0.51
}
```

이벤트 row 예:

```json
{
  "feature_id": "embedding_distance",
  "start": "2026-06-24T08:00:00Z",
  "end": "2026-06-24T12:00:00Z",
  "level": "warning",
  "score": 0.68,
  "label": "warning signal"
}
```

## 4. Data Binding 방식

방식 A: feature별 source 분리

```json
{
  "features": [
    {
      "feature_id": "embedding_distance",
      "label": "임베딩 거리",
      "unit": "distance",
      "timeseries_source": "chart.metric.embedding_distance.timeseries",
      "event_source": "chart.metric.embedding_distance.drift_events"
    }
  ]
}
```

방식 B: 하나의 source 안에 feature field 포함

```json
{
  "timeseries_source": "chart.metric.feature_timeseries",
  "feature_field": "feature_id",
  "time_field": "bucket_start",
  "value_field": "mean"
}
```

## 5. Tick 계산 세부

기본값:

```text
min_label_px = 78
max_tick_count = 8
min_tick_interval = 1h
```

계산:

```text
max_ticks_by_width = floor(plot_width / min_label_px)
max_ticks = min(max_tick_count, max_ticks_by_width)
```

후보:

```text
1h
3h
6h
12h
1d
3d
1w
2w
1M
3M
6M
1y
2y
5y
```

선택 규칙:

```text
visible_span / interval <= max_ticks
조건을 만족하는 가장 작은 interval 선택
```

## 6. 시간 범위별 라벨 예

| visible range | tick interval 예 | label format 예 |
|---|---|---|
| 5년 이상 | 1y, 2y, 5y | `2026` |
| 1년 ~ 5년 | 3M, 6M, 1y | `2026-06` |
| 3개월 ~ 1년 | 1M, 3M | `06월` 또는 `2026-06` |
| 1개월 ~ 3개월 | 1w, 2w | `06-24` |
| 1주 ~ 1개월 | 1d, 3d | `06-24` |
| 1일 ~ 1주 | 6h, 12h, 1d | `06-24 12:00` |
| 1일 이하 | 1h, 3h, 6h | `09:00` 또는 `06-24 09:00` |

## 7. Cache와 요청

cache key 예:

```text
model_id + feature_id + from + to + source_resolution + filters
```

batch 요청 예:

```text
model_id
features = [embedding_distance, token_length, refusal_rate]
from
to
source_resolution
filters
```

정책:

```text
서버가 batch feature 요청을 지원하면 같은 visibleDomain/sourceResolution으로 한 번에 요청한다.
지원하지 않으면 feature별 요청을 병렬로 수행한다.
한 feature 요청 실패가 전체 컴포넌트 실패가 되면 안 된다.
```

## 8. 테스트 시나리오

권장 테스트:

```text
시간 이동 -> 범위 조정 -> 스케일 조정 -> 다시 시간 이동
빠른 범위 선택 -> 직접 날짜/시간 선택 -> 전체 보기
긴 범위에서 hour scale 선택
짧은 범위에서 month scale 선택
plot width 변경 후 tick label 재계산
확대 popup 진입 후 displayBucket/tick 재계산
comparison feature 추가 후 모든 panel의 x축이 동일함
primary feature 변경 후 visibleDomain이 유지됨
한 feature 데이터 실패 시 나머지 feature panel은 유지됨
feature별 y축 단위가 다를 때 y축을 공유하지 않음
```

# 드리프트 지표 시계열 컴포넌트 기능 요구사항

작성일: 2026-06-24

## 0. 핵심 전제

`drift_metric_timeseries`는 드리프트 여부와 장기 추세를 확인하기 위한 컴포넌트다.
초 단위나 분 단위의 고빈도 원시 데이터를 분석하거나 실시간 스트리밍을 시각화하는 도구가 아니다.

서버는 기본 원천 데이터를 시간 단위(`1h`) bucket으로 제공하고, UI가 기본으로 보여주는 화면은 일 단위(`1d`) 요약/평균 데이터다.
사용자가 시간 단위 상세 보기를 선택할 수는 있지만, 시간 단위 표시는 과도한 범위를 허용하지 않고 최대 7일 이내로 제한한다.
월/연 스케일은 드리프트의 장기 추세를 읽기 위한 x축 구분 방식이며, 초/분 단위 정밀 분석을 의미하지 않는다.

## 1. 개요

`drift_metric_timeseries`는 인공지능 모델의 추론 결과에서 발생하는 feature별 드리프트 지표를 시간축으로 보여주는 컴포넌트다.

기본은 하나의 primary feature를 표시한다. 사용자가 비교 feature를 추가하면 같은 시간 범위와 같은 x축 스케일로 여러 feature 그래프를 위아래로 함께 표시한다.

## 2. 핵심 범위

필수 기능:

```text
시간축 x + 지표값 y 시계열 표시
primary feature 선택
comparison feature 추가/제거
공유 시간축 기반 다중 feature 비교
warning/drift 이벤트 표시
시간 범위 선택
시간 스케일 선택
tooltip
확대 팝업
```

1차 범위에서 제외:

```text
분 단위 이하 실시간 streaming
raw point 전체 표시
복잡한 anomaly explanation
서로 다른 시간 범위를 가진 독립 chart grid
drilldown workflow
event click action
```

## 3. 입력 데이터

기본 입력은 raw event stream이 아니라 집계된 time bucket series다.

필수 필드:

| field | 설명 |
|---|---|
| `bucket_start` | bucket 시작 시각 |
| `value` 또는 `mean` | 표시할 대표 지표값 |
| `feature_id` | feature 식별자 |

권장 필드:

| field | 설명 |
|---|---|
| `bucket_end` | bucket 종료 시각 |
| `resolution` | 서버 집계 해상도 |
| `count` | bucket 안 원본 샘플 수 |
| `min`, `max` | 변동 범위 |
| `unit` | feature 값 단위 |
| `status` | `observed`, `missing`, `closed`, `imputed`, `partial` 중 bucket 상태 |
| `coverage` | bucket의 데이터 충족 비율 |

## 4. Drift 이벤트

서버가 탐지한 drift 이벤트는 feature별로 연결한다.

필수 level:

| level | 의미 |
|---|---|
| `normal` | 정상 |
| `warning` | 약한 드리프트 신호 |
| `drift` | 확정 또는 강한 드리프트 |

이벤트는 점 또는 구간으로 표시할 수 있다.

```text
point event -> marker
interval event -> vertical band
warning -> 약한 색상
drift -> 강한 색상
```

## 5. Feature 비교

기본 동작:

```text
primary feature 하나를 먼저 표시한다.
comparison feature는 사용자가 추가한다.
comparison feature를 제거해도 primary feature와 현재 시간 상태는 유지한다.
```

모든 feature가 공유하는 값:

```text
visible range
time scale
tick interval
label format
display bucket
navigator selection
pan/zoom/range selector 상태
```

feature별로 독립인 값:

```text
y축 범위
단위
threshold
warning/drift 이벤트
line/band 색상
loading/error/empty 상태
```

서로 단위가 다른 feature를 하나의 y축에 겹쳐 그리지 않는다.

## 6. 시간 범위와 스케일

지원 스케일:

```text
auto
hour
day
month
year
```

지원 시간 조작:

```text
빠른 범위 preset
시작/종료 날짜와 시간 직접 선택
navigator/brush
pan/zoom
이전/다음 구간 이동
전체 보기
```

권장 preset:

```text
오늘
최근 24시간
최근 7일
최근 30일
최근 3개월
최근 1년
전체
직접 선택
```

범위, 스케일, 집계 단위는 분리해서 처리한다.

```text
범위: 사용자가 보고 싶은 시작/종료 시각
스케일: x축을 시간/일/월/연 중 어떤 단위로 읽을지
집계 단위: 값을 어떤 bucket 평균으로 표시할지
```

## 7. 집계

서버는 가능하면 집계 데이터를 제공한다.

권장 서버 해상도:

```text
1h
1d
1w
1M
```

UI는 현재 visible range와 화면 폭에 맞춰 서버 집계 데이터를 추가 압축할 수 있다.

평균 재집계는 count 기반 weighted mean을 사용한다.

```text
weighted_mean = sum(mean_i * count_i) / sum(count_i)
```

결측 처리 원칙:

```text
UI는 missing bucket을 0이나 주변값으로 몰래 보간하지 않는다.
missing은 선을 끊거나 결측 구간으로 표시한다.
closed는 주말/휴무/라인 정지처럼 기대 데이터가 없는 구간으로 처리할 수 있다.
imputed는 서버가 보간한 값이므로 실제 관측값과 구분한다.
partial은 coverage가 낮은 불완전 bucket으로 표시한다.
```

상태별 의미:

| status | 의미 |
|---|---|
| `observed` | 실제 관측 데이터 있음 |
| `missing` | 기대했지만 데이터 없음 |
| `closed` | 비운영 시간이라 데이터가 없어도 되는 구간 |
| `imputed` | 서버가 보간/대체한 값 |
| `partial` | 일부 데이터만 들어온 불완전 bucket |

## 8. 상태와 렌더링 원칙

컴포넌트는 하나의 `timeState`를 가진다.

```text
timeState가 바뀌면 모든 feature panel을 같은 x축으로 다시 렌더링한다.
feature 추가/제거는 timeState를 바꾸지 않는다.
feature panel은 timeState를 직접 수정하지 않는다.
```

자세한 상태 모델은 [state_model.md](./state_model.md)를 따른다.

## 9. 성능

기본 정책:

```text
raw point 전체를 직접 렌더링하지 않는다.
현재 visible range와 plot width를 기준으로 표시 point 수를 제한한다.
화면 pixel보다 point가 많으면 bucket 집계를 사용한다.
cache 범위 안의 pan/zoom은 서버 재요청 없이 처리할 수 있어야 한다.
```

## 10. 최소 Config

```json
{
  "componentType": "drift_metric_timeseries",
  "config": {
    "primary_feature": "embedding_distance",
    "comparison_features": [],
    "feature_field": "feature_id",
    "time_field": "bucket_start",
    "end_time_field": "bucket_end",
    "value_field": "mean",
    "count_field": "count",
    "source_resolution": "1h",
    "display_bucket": "auto",
    "aggregation_method": "weighted_mean",
    "range_presets": ["24H", "7D", "30D", "3M", "1Y", "ALL"]
  }
}
```

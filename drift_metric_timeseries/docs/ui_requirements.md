# 드리프트 지표 시계열 컴포넌트 UI 요구사항

작성일: 2026-06-24

## 1. UI 목표

`drift_metric_timeseries`는 사용자가 한 feature의 드리프트 추세를 보다가, 필요한 feature를 같은 시간축으로 추가해 비교할 수 있어야 한다.

핵심 목표:

```text
현재 보고 있는 시간 범위와 스케일을 잃지 않게 한다.
x축 라벨이 겹치지 않게 한다.
warning과 drift를 명확히 구분한다.
feature별 값 범위가 달라도 비교가 가능하게 한다.
작은 panel과 확대 popup 모두에서 읽을 수 있어야 한다.
```

## 2. 기본 화면 구조

권장 구조:

```text
header
  title
  primary feature selector
  comparison feature add/remove
  current state summary
  quick range controls
  scale selector
  expand button

plot
  stacked feature panels
    feature title
    independent y-axis
    line/band
    warning/drift marker or region
  shared x-axis

footer
  navigator / overview
```

## 3. 상태 요약

사용자가 현재 무엇을 보고 있는지 항상 보여준다.

예:

```text
2026-06-01 09:00 ~ 2026-06-08 18:00 · 7일 9시간 · 시간 축 · 1시간 평균 · warning 3 / drift 1
```

포함할 정보:

```text
현재 시간 범위
범위 길이
축 스케일
집계 단위
현재 범위 안 warning/drift 개수
표시 중인 feature 수
```

## 4. 시간 탐색 컨트롤

필수 컨트롤:

```text
빠른 범위: 24시간, 7일, 30일, 3개월, 1년, 전체
직접 선택: 시작/종료 날짜와 시간
스케일: 자동, 시간, 일, 월, 연
이동: 이전 구간, 다음 구간
전체 위치: navigator / overview
```

범위와 스케일은 분리해서 보여준다.

```text
범위: 2026-06-01 09:00 ~ 2026-06-08 18:00
스케일: 시간 축
집계: 1시간 평균
```

작은 panel에서는 빠른 범위와 직접 선택을 compact menu로 접을 수 있다. 단, 상태 요약은 숨기지 않는다.

## 5. Feature 비교 UI

기본 화면은 primary feature 하나만 표시한다.

```text
Feature: [임베딩 거리 v]   [+ 비교 feature]
```

comparison feature를 추가하면 같은 시간 상태를 공유하는 panel을 아래에 추가한다.

```text
임베딩 거리
  line + band + warning/drift

토큰 길이                  [제거]
  line + band + warning/drift

거절률                    [제거]
  line + band + warning/drift

shared x-axis
navigator
```

필수 규칙:

```text
primary feature는 하나다.
comparison feature는 0개 이상 추가할 수 있다.
모든 feature panel은 같은 x축 시간 범위와 tick을 사용한다.
각 feature panel은 독립 y축을 가진다.
x축 라벨은 기본적으로 가장 아래 panel에만 표시한다.
hover guide line은 모든 panel에 동기화한다.
```

비교 feature가 많아 panel 내용이 잘리면 세로 스크롤을 허용한다.

## 6. X축 라벨

원칙:

```text
데이터 row마다 x축 라벨을 표시하지 않는다.
현재 visible range와 plot width 기준으로 tick 개수를 제한한다.
라벨이 겹치면 tick 수를 줄인다.
label 회전은 최후 수단으로만 사용한다.
```

권장 tick 후보:

```text
1h, 3h, 6h, 12h, 1d, 3d, 1w, 2w, 1M, 3M, 6M, 1y
```

라벨 겹침 방지 우선순위:

```text
1. tick interval을 크게 한다.
2. label format을 짧게 한다.
3. 첫/마지막 label을 우선 유지한다.
4. 일부 중간 label을 숨긴다.
5. 그래도 불가능하면 30도 이하 회전을 허용한다.
```

## 7. Drift 표시

warning과 drift는 색상과 강도로 구분한다.

```text
warning: 연한 amber 계열
drift: 강한 red/crimson 계열
```

표시 방식:

```text
point event -> marker
interval event -> vertical band
```

색만으로 의미를 전달하지 않고 tooltip에도 level을 표시한다.

## 8. Tooltip

기본 tooltip:

```text
bucket start/end
value 또는 mean
count
drift level
```

다중 feature 비교에서는 hover timestamp를 동기화한다.

```text
현재 panel tooltip에는 해당 feature 값을 표시한다.
모든 panel에는 같은 timestamp의 vertical guide를 표시한다.
```

통합 tooltip은 후순위 기능으로 둔다.

## 9. Empty / Loading / Error

feature별 상태를 독립적으로 표시한다.

```text
한 feature 데이터가 없어도 다른 feature panel은 유지한다.
실패한 feature panel만 error 상태로 표시한다.
전체 컴포넌트가 실패한 것처럼 보이면 안 된다.
```

## 10. Missing / Closed / Imputed 표시

결측은 숨기지 않는다.

```text
missing: 선을 끊고 결측 구간으로 표시
closed: 휴무/비운영 구간으로 연하게 표시하거나 coverage 계산에서 제외
imputed: 값은 표시하되 점선/별도 marker로 실제 관측값과 구분
partial: tooltip과 요약에 낮은 coverage 표시
```

상태 요약이나 panel 요약에는 coverage를 표시한다.

예:

```text
coverage 82% · missing 6 · closed 8 · imputed 2 · partial 3
```

## 11. 접근성

요구사항:

```text
range selector button은 텍스트 label을 가진다.
warning/drift는 tooltip이나 legend에도 level을 표시한다.
keyboard로 feature 선택, 비교 feature 제거, range selector, 확대 버튼을 사용할 수 있다.
```

## 12. 최소 UI Config

```json
{
  "feature_compare": {
    "enabled": true,
    "max_comparison_features": 5,
    "layout": "stacked",
    "shared_time_axis": true,
    "shared_y_axis": false,
    "sync_hover": true,
    "x_axis_labels": "bottom_only"
  },
  "time_axis": {
    "scale": "auto",
    "max_tick_count": 8,
    "min_label_px": 78,
    "label_collision": "reduce_ticks"
  },
  "range_selector": {
    "enabled": true,
    "presets": ["24H", "7D", "30D", "3M", "1Y", "ALL"],
    "date_time_picker": true
  },
  "navigator": {
    "enabled": true
  }
}
```

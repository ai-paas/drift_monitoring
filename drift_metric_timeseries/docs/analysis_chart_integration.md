# 분석 차트 연동 가이드

작성일: 2026-06-24

이 문서는 `drift_metric_timeseries`에서 warning/drift 이벤트를 눌렀을 때 재생성 차트를 분석 팝업으로 여는 방식의 기준을 정의한다.

## 핵심 원칙

분석 팝업은 이미 만들어진 chart payload를 재사용해야 한다.

```text
saved chart payload
  layout + components + config + text
        +
event analysis data
        +
runtime config override
        =
runtime render payload
```

서버는 새 차트를 만들거나 chart definition을 재조립하지 않는다. 서버는 이벤트 시점에 맞는 `data`와 필요한 runtime config override를 계산해 렌더러에 전달한다. 이때 저장된 chart definition 자체를 수정하면 안 된다.

## 반드시 유지할 것

분석 API는 원본 재생성 차트의 다음 필드를 그대로 유지한다.

- `layout`
- `components`
- component `config`
- `title`
- `originalPath`
- `reproduction`
- area `title`
- area `description`
- notes/legend의 문구와 표시 방식

이 필드들은 Chart Builder가 만든 차트 정의다. 이벤트 분석 API가 저장된 definition을 직접 바꾸기 시작하면 “컴포넌트에 새 데이터와 runtime 설정이 들어왔을 때 동작하는지”를 검증할 수 없다.

## 서버가 바꿀 수 있는 것

분석 API가 바꿀 수 있는 값은 원칙적으로 `data`와 별도 `runtimeConfig`뿐이다.

허용:

- `payload.data[sourceKey]`의 row 배열 교체
- row 값, label, displayValue 교체
- 이벤트 시점에 해당하는 marker row 추가
- 현재까지 수신한 데이터만 반영하도록 row 범위 제한
- tenant, feature, event window에 맞춘 runtime config override 생성
- threshold, marker 위치, axis domain 정책 파라미터, annotation value 같은 실행 시점 값 전달

조건부 허용:

- `chartId`를 runtime instance 구분용으로 suffix 처리하는 것
- 단, 원본 chart identity가 필요한 곳에서는 base chart id를 별도 보존해야 한다.
- runtime config override를 payload와 함께 보내는 것
- 단, override는 저장된 component 구조를 변경하지 않고 기존 component instance에 병합되는 값이어야 한다.

금지:

- `layout.rows`, `gridTemplateRows`, `areas` 변경
- component 추가/삭제
- component type 변경
- 저장된 component `config`를 직접 덮어쓰기
- 원본 한글 title, description, notes, legend를 서버에서 새 문구로 교체
- 분석 대상 feature에 따라 서버가 다른 차트 구조를 즉석에서 조립

## Runtime Config Override

실제 운영에서는 드리프트 시점, 고객사 설정, 모델/feature별 기준에 따라 threshold, marker, 축 domain 정책, annotation 값이 달라질 수 있다. 이런 값은 chart definition 수정이 아니라 runtime override로 처리한다.

권장 구조:

```json
{
  "payload": {
    "chartId": "CHART-MV-002",
    "layout": {},
    "components": [],
    "data": {}
  },
  "runtimeConfig": {
    "componentOverrides": {
      "CHART-MV-002.mmd.0": {
        "horizontal_markers": [
          {"y": 0.18, "label": "관리 기준 0.18"}
        ]
      }
    },
    "themeOverrides": {
      "tenantAccent": "teal"
    }
  }
}
```

병합 규칙:

- override는 component instance id 기준으로 기존 `config`에 얕게 또는 명시 정책에 따라 병합한다.
- override는 `componentType`, `area`, `dataBinding`, `layout`을 바꾸지 못한다.
- override는 렌더 직전 메모리에서만 적용하고 저장된 payload에는 쓰지 않는다.
- 고객사별 기본값은 tenant profile이나 runtime request context에서 오며, Chart Builder 산출물을 수정하지 않는다.

## 축과 범위 처리

새 데이터가 들어왔을 때 축 범위가 맞지 않으면 저장된 `config`를 덮어쓰지 않는다. 고정 축이 아니라 실행 시점 축 조정이 필요한 차트는 runtime config override 또는 component의 auto domain 정책으로 처리한다.

컴포넌트는 다음 중 하나를 지원해야 한다.

- `config`에 명시된 고정 domain을 사용한다.
- `config`가 `auto` 정책을 갖고 있으면 들어온 data로 domain을 계산한다.
- `runtimeConfig`가 domain override를 제공하면 렌더 시점에만 병합한다.
- data row에 포함된 값만으로 화면을 그릴 수 없으면 component contract를 보완한다.

즉, 이벤트 분석 API가 저장된 payload 안의 `x_max`, `y_max`, `x_ticks`, `horizontal_markers`, `annotations`를 매번 직접 고쳐야만 화면이 맞는다면 해당 chart component는 재사용 가능한 형태가 아니다. 필요한 값은 runtime override로 넘기거나 renderer contract를 보완한다.

## 노트와 설명

분석 팝업의 노트는 원본 chart payload에 들어 있는 notes component와 data source를 사용한다.

이벤트 날짜, 수신 구간, score 같은 동적 설명이 꼭 필요하면 다음 중 하나로 처리한다.

- 원본 notes data source의 row 값만 교체한다.
- 별도 summary data source에 동적 값을 넣고, 기존 decision-card가 그 값을 표시하게 한다.

서버가 원본 노트 컴포넌트를 다른 component type으로 바꾸거나, 원본 한글 설명을 영어 샘플 문구로 교체하지 않는다.

## 구현 체크리스트

분석 API를 수정할 때 확인한다.

- 원본 payload를 deep clone한 뒤 `data` 외 필드를 변경하지 않았는가?
- runtime config 변경이 필요하면 저장 payload가 아니라 별도 override로 분리했는가?
- `layout` diff가 없는가?
- `components` diff가 없는가?
- 저장된 component `config` diff가 없는가?
- 기존 gallery에서 보이던 한글 제목, 설명, note, legend가 유지되는가?
- `knownEnd` 이후 미래 데이터가 payload에 포함되지 않는가?
- 데이터 row 수가 1개여도 component가 깨지지 않는가?

## 분석 API 적용 원칙

과거 prototype에서는 `chart_builder_server.py`가 `/api/drift-metric-timeseries/events/analyze`를 제공했다. 이 endpoint는 Chart Builder 본 기능과 무관한 demo bridge였으므로 제거한다.

운영 또는 통합 데모의 event analysis API는 Drift Server가 제공해야 하며, 다음 구조를 따라야 한다.

```text
1. feature/event/knownEnd로 분석 window의 data row를 만든다.
2. 연결할 base chart id를 선택한다.
3. `web/recreated_chart_payloads.js`에서 base chart payload를 deep clone한다.
4. clone의 `data`만 이벤트 window용 row로 교체한다.
5. threshold/marker/axis 정책처럼 실행 시점 설정이 필요하면 `runtimeConfig`로 분리한다.
6. `ChartRuntime.renderChartPayload()`에 payload와 runtime override를 함께 넘긴다.
```

이 구조에서 차트가 깨지면 서버에서 차트 정의를 덮어써서 맞추지 말고, 해당 component renderer나 saved chart payload의 data binding contract를 고친다.

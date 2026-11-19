# Chart Builder UI Design

작성일: 2026-06-17

## 1. 목적

Chart Builder는 구현된 chart component 목록을 보고, semantic area 기반 container에 component를 배치해 완전한 chart를 만들 수 있게 하는 화면이다.

사용자는 chart HTML/JS를 직접 작성하지 않고 다음 작업을 UI에서 수행한다.

```text
component 선택
-> 배치 영역 선택
-> component config 설정
-> data binding 설정
-> preview 확인
-> 저장
```

이 문서는 Chart Builder의 화면 구조, 사용자 흐름, 상태 모델, 저장 구조, API 계약을 정의한다.

## 1.1 Build 방식 결정

Chart Builder의 build 결과는 React/TypeScript 코드 파일이 아니라 DB에 저장되는 chart definition runtime payload다.

권장 방식:

```text
Chart Builder에서 배치/설정
  -> DB에 layout + component instance + config + data binding 저장
  -> Chart Renderer가 DB 설정을 조회
  -> component registry에서 renderer 선택
  -> React component를 런타임에 조립
  -> 완전한 chart 화면 출력
```

즉 build는 code generation이 아니라 **runtime render 가능한 chart configuration 저장**이다.

이 방식을 기본으로 채택한다.

```text
기본: DB layout/config 기반 runtime render
옵션: chart JSON export
나중: React TSX code export
```

초기 구현에서는 React TSX code export를 만들지 않는다.

## 2. 기본 화면 구조

Chart Builder는 세 영역으로 구성한다.

```text
+----------------------+-------------------------------+----------------------+
| Component Palette    | Chart Container               | Properties           |
|----------------------|-------------------------------|----------------------|
| trend_line           | summary                       | selected item        |
| threshold_line       | [summary_metric_panel]        | config               |
| bar_chart            |                               | data binding         |
| event_marker         | main                          | layout / overflow    |
| state_timeline       | [trend_line + overlays]       | validation           |
| distribution_view    |                               |                      |
|                      | side_top                      |                      |
|                      | [bar_chart]                   |                      |
|                      | side_bottom                   |                      |
|                      | [state_timeline]              |                      |
+----------------------+-------------------------------+----------------------+
```

| 영역 | 역할 |
|---|---|
| Component Palette | 구현된 component type 목록 표시 |
| Chart Container | semantic area와 배치된 component preview 표시 |
| Properties | 선택된 area 또는 component instance의 설정 편집 |

## 3. Component Palette

왼쪽 palette는 구현 완료된 component type만 보여준다.

초기 MVP에서는 다음 component를 우선 표시한다.

```text
trend_line
threshold_line
event_marker
bar_chart
detector_statistic_view
state_timeline
reference_current_comparison
distribution_view
```

각 palette item은 다음 정보를 가진다.

| 항목 | 설명 |
|---|---|
| component_code | `bar_chart`, `trend_line` 등 |
| display_name | 사용자에게 보이는 이름 |
| status | implemented, draft, deprecated |
| supported_area_roles | 배치 가능한 area role |
| overlay_capable | overlay 가능 여부 |
| required_bindings | 필수 data binding 목록 |

Palette item 예:

```json
{
  "component_code": "bar_chart",
  "display_name": "Bar Chart",
  "status": "implemented",
  "supported_area_roles": ["primary_visual", "secondary_visual"],
  "overlay_capable": false,
  "required_bindings": ["category_field", "value_field"]
}
```

## 4. Chart Container

Chart Container는 완전한 바둑판 grid가 아니라 semantic area layout을 보여준다.

사용자에게 보이는 area:

```text
summary
main
side_top
side_bottom
notes
legend
```

내부 저장은 grid 좌표다.

```json
{
  "area": "main",
  "role": "primary_visual",
  "x": 0,
  "y": 1,
  "w": 8,
  "h": 5
}
```

Container 동작:

- area 선택
- area 이동
- area 크기 조절
- area 추가
- area 삭제
- area role 변경
- component instance drop
- overlay component 배치
- area별 overflow policy 확인

## 5. Component 배치 방식

Component를 배치하는 방법은 두 가지를 지원한다.

### 5.1 Drag and Drop

Palette에서 component를 끌어 Chart Area 위에 놓는다.

```text
bar_chart drag
-> side_top drop
-> component instance 생성
-> Properties panel에 config 표시
```

Prototype에서 HTML5 native drag/drop이 버튼 요소와 일부 브라우저 환경에서 안정적으로 동작하지 않는 문제가 있었다. 이후 구현에서는 다음 중 하나를 선택한다.

```text
권장: pointer event 기반 custom drag
대안: dnd-kit 또는 react-grid-layout의 drag layer
비권장: button draggable=true만 사용하는 native drag/drop 단독 의존
```

Prototype에서 검증된 pointer drag 동작:

```text
palette item pointerdown
-> drag ghost 생성
-> pointermove에서 elementFromPoint로 chart area 탐색
-> area drag-over highlight
-> pointerup 시 해당 area에 component 배치
```

드래그 중에는 사용자가 배치 대상을 알 수 있도록 area highlight를 표시한다.

```text
drag-over area
  -> border 강조
  -> background 강조
  -> drop 가능 상태 표시
```

### 5.2 선택 후 배치

마우스 drag가 불편한 경우를 위해 선택 기반 배치도 제공한다.

```text
component 선택
-> area 선택
-> "이 영역에 추가" 버튼
```

선택 기반 배치는 접근성과 안정성 측면에서 필요하다.

### 5.3 이미 component가 있는 영역에 drop

이미 base component가 있는 영역에 새 base component를 drop하면 기존 base component를 교체한다.

```text
top_left: trend_line
bar_chart drop to top_left
-> trend_line 제거
-> bar_chart 배치
```

Overlay component는 기존 base component를 지우지 않고 같은 area에 추가한다.

```text
bottom_left: detector_statistic_view
threshold_line drop to bottom_left
-> detector_statistic_view 유지
-> threshold_line overlay 추가
```

이 규칙은 사용자가 drag/drop을 \"배치 또는 교체\" 동작으로 자연스럽게 이해하게 하기 위한 것이다.

## 6. Area와 Component 관계

하나의 area에는 여러 component가 들어갈 수 있다.

두 가지 방식이 있다.

| 방식 | 설명 | 예 |
|---|---|---|
| stacked | area 안에서 component를 위아래 또는 순서대로 배치 | summary metric 여러 개 |
| overlay | 같은 좌표계 위에 겹쳐서 표시 | trend_line + threshold_line + event_marker |

예:

```json
[
  {
    "component_type": "trend_line",
    "area": "main",
    "is_overlay": false,
    "z_index": 10
  },
  {
    "component_type": "threshold_line",
    "area": "main",
    "is_overlay": true,
    "z_index": 20
  },
  {
    "component_type": "event_marker",
    "area": "main",
    "is_overlay": true,
    "z_index": 30
  }
]
```

Overlay component는 base component의 scale context를 공유해야 한다.

```text
trend_line이 x/y scale 생성
threshold_line이 y scale 사용
event_marker가 x scale 사용
```

## 7. Properties Panel

오른쪽 Properties panel은 선택 대상에 따라 내용이 바뀐다.

### 7.1 Area 선택 시

| 설정 | 설명 |
|---|---|
| area_code | `main`, `side_top` 등 |
| role | primary_visual, secondary_visual 등 |
| x, y, w, h | grid 좌표 |
| min_w, min_h | 최소 크기 |
| overflow_policy | fit, scroll_x, scroll_y, fit_or_scroll |
| title_visible | area 제목 표시 여부 |

### 7.2 Component 선택 시

| 설정 | 설명 |
|---|---|
| component_type | component 종류 |
| area | 배치 area |
| display_order | stacked 순서 |
| z_index | overlay 순서 |
| is_overlay | overlay 여부 |
| config_json | 렌더링 설정 |
| data_binding_json | 데이터 field mapping |
| visible | 표시 여부 |
| overflow_policy | component별 overflow override |

## 8. Config 편집

Config는 component type별 schema를 기반으로 form을 만든다.

예: `bar_chart`

```json
{
  "orientation": "horizontal",
  "category_field": "feature_name",
  "value_field": "drift_score",
  "highlight_rule": "max_value",
  "sort_order": "value_desc"
}
```

Form 표현:

| config | UI control |
|---|---|
| orientation | segmented control |
| category_field | field select |
| value_field | field select |
| highlight_rule | select |
| sort_order | select |

Config 변경 시 preview는 즉시 갱신한다.

## 9. Data Binding 편집

Component가 완전한 chart로 동작하려면 data binding이 필요하다.

예:

```json
{
  "source": "algorithm_result",
  "category_field": "feature_name",
  "value_field": "contribution_value"
}
```

Data Binding panel은 다음을 보여준다.

| 항목 | 설명 |
|---|---|
| source | algorithm_result, chart_input_json, static_example |
| available_fields | 현재 데이터에서 선택 가능한 field |
| required_fields | component가 요구하는 field |
| mapped_fields | 사용자가 연결한 field |
| validation_status | valid, missing_required_field, type_mismatch |

필수 binding이 없으면 chart preview에는 `missing data` 상태를 표시한다.

## 10. Preview 정책

Preview는 저장 전에도 항상 가능한 범위에서 표시한다.

Preview mode:

| mode | 설명 |
|---|---|
| live | config 변경 즉시 재렌더링 |
| compact preview | 작은 area에서는 label 축소/생략 |
| missing data | 필수 field가 없을 때 상태 표시 |
| scroll preview | overflow policy에 따라 내부 scroll 표시 |

Preview는 iframe이 아니라 React component renderer로 표시한다.

## 11. Responsive 규칙

Chart Builder에서 가장 중요한 조건은 영역 크기가 바뀌어도 그림과 글씨가 깨지지 않는 것이다.

공통 규칙:

```text
component는 고정 px 크기를 갖지 않는다.
ResizeObserver로 area의 실제 width/height를 받는다.
axis, label, legend, tick 수는 크기에 따라 줄인다.
너무 작으면 compact 또는 summary_only mode로 전환한다.
필요하면 scroll_x 또는 scroll_y를 생성한다.
```

Component renderer는 다음 값을 받는다.

```ts
type ResponsiveRenderContext = {
  width: number;
  height: number;
  mode: "normal" | "compact" | "summary_only" | "scroll";
  minReadableFontPx: number;
};
```

Prototype에서 확인된 추가 규칙:

```text
1. component는 배치된 area를 100% 채워야 한다.
2. renderer가 임의 최소 width/height로 chart를 키우면 안 된다.
3. area가 작을 때는 chart 자체를 키우는 대신 compact/summary_only mode로 전환한다.
4. single component와 multiple component의 wrapper 구조를 다르게 만들면 높이 계산 오류가 생긴다.
5. single component도 component-stack 안에 넣어 wrapper 구조를 통일한다.
6. summary_only mode에서도 component의 primary label/value는 숨기지 않는다.
7. 최소 판독 크기보다 작은 영역에서는 chart를 더 찌그러뜨리지 않고 내부 scroll을 만든다.
```

`threshold_line` 사례처럼 작은 영역에서 label을 모두 숨기면 component의 의미가 사라진다. 따라서 Builder renderer는 label priority를 구분해야 한다.

```text
primary
  - component 의미를 구성하는 핵심 label/value
  - summary_only에서도 유지

secondary
  - axis label, 일부 tick, 보조 수치
  - compact에서 일부 생략 가능

decorative
  - legend 보조 설명, point label, grid text
  - compact/summary_only에서 생략 가능
```

`bar_chart`처럼 항목 수가 있는 component는 항목별 최소 row height를 가진다. 영역 높이가 부족하면 마지막 항목을 자르지 않고 component stage에 세로 scroll을 만든다.

```text
area stage height < component minRenderHeight
  -> render surface height = minRenderHeight
  -> stage overflow-y = auto
```

가로도 동일하다.

```text
area stage width < component minRenderWidth
  -> render surface width = minRenderWidth
  -> stage overflow-x = auto
```

이 규칙은 다음 문제를 막기 위한 것이다.

```text
bar_chart의 마지막 category label이 잘림
긴 x-axis label이 chart 밖으로 나감
heatmap column이 너무 좁아져 판독 불가
table/ranking row가 겹침
```

## 12. 저장 모델

Chart Builder 저장 payload:

```json
{
  "chart_id": "CHART-CUSTOM-001",
  "layout": {
    "preset_code": "default_3_panel",
    "columns": 12,
    "rows": 8,
    "areas": [
      { "area": "summary", "role": "summary", "x": 0, "y": 0, "w": 12, "h": 1 },
      { "area": "main", "role": "primary_visual", "x": 0, "y": 1, "w": 8, "h": 5 }
    ]
  },
  "components": [
    {
      "component_instance_id": "main_trend_1",
      "component_type": "trend_line",
      "area": "main",
      "is_overlay": false,
      "z_index": 10,
      "config": {},
      "data_binding": {}
    }
  ]
}
```

DB 저장 대상:

```text
chart_layout_override
chart_component_instance
```

이 payload가 Chart Builder의 build artifact다. 별도 `chart_xxx.tsx` 파일을 생성하지 않는다.

Renderer는 저장된 payload를 읽어서 component를 조립한다.

```text
GET /api/chart-builder/charts/{chart_id}
  -> layout + components + data binding 조회
  -> React renderer가 component registry로 렌더링
```

## 12.1 Runtime Render Payload

런타임 renderer가 받는 payload는 다음 형태를 기준으로 한다.

```json
{
  "chartId": "CHART-CUSTOM-001",
  "layout": {
    "layoutType": "semantic_grid",
    "columns": 12,
    "rows": 8,
    "areas": [
      { "area": "summary", "role": "summary", "x": 0, "y": 0, "w": 12, "h": 1 },
      { "area": "main", "role": "primary_visual", "x": 0, "y": 1, "w": 8, "h": 5 }
    ]
  },
  "components": [
    {
      "componentInstanceId": "main_bar_1",
      "componentType": "bar_chart",
      "area": "main",
      "isOverlay": false,
      "zIndex": 10,
      "config": {
        "orientation": "horizontal",
        "category_field": "feature_name",
        "value_field": "drift_score"
      },
      "dataBinding": {
        "source": "algorithm_result",
        "category_field": "feature_name",
        "value_field": "drift_score"
      }
    }
  ],
  "data": {
    "algorithm_result": []
  }
}
```

Renderer는 `componentType`을 기준으로 component registry에서 구현체를 찾는다.

```ts
const componentRegistry = {
  bar_chart: BarChart,
  trend_line: TrendLine,
  threshold_line: ThresholdLine,
  event_marker: EventMarker
};
```

Renderer는 저장된 config와 data binding을 props로 넘긴다.

```text
BarChart
  width
  height
  data
  config
  theme
```

따라서 chart 수정은 code deploy 없이 DB 설정 변경만으로 반영된다.

## 13. API 계약

FastAPI에 필요한 API:

```text
GET  /api/chart-builder/component-types
GET  /api/chart-builder/layout-presets
GET  /api/chart-builder/charts/{chart_id}
PUT  /api/chart-builder/charts/{chart_id}
POST /api/chart-builder/charts/{chart_id}/preview
POST /api/chart-builder/charts
GET  /api/charts/{chart_id}/runtime-render-payload
```

### 13.1 Component type 목록

```text
GET /api/chart-builder/component-types
```

응답:

```json
{
  "ok": true,
  "componentTypes": [
    {
      "component_code": "bar_chart",
      "display_name": "Bar Chart",
      "status": "implemented",
      "supported_area_roles": ["primary_visual", "secondary_visual"],
      "overlay_capable": false,
      "parameter_schema": {}
    }
  ]
}
```

### 13.2 Chart Builder 상태 조회

```text
GET /api/chart-builder/charts/CHART-CTRL-002
```

응답:

```json
{
  "ok": true,
  "chart": {
    "chart_id": "CHART-CTRL-002",
    "layout": {},
    "components": [],
    "available_data_fields": []
  }
}
```

### 13.3 저장

```text
PUT /api/chart-builder/charts/CHART-CTRL-002
```

요청 body는 저장 모델과 같다.

저장 시 검증:

```text
area_code 중복 없음
area 좌표가 layout 범위 안에 있음
component area가 존재함
component_type이 구현되어 있음
필수 config 존재
필수 data binding 존재
overlay component가 scale provider를 찾을 수 있음
```

### 13.4 Runtime Render Payload 조회

```text
GET /api/charts/CHART-CTRL-002/runtime-render-payload
```

응답:

```json
{
  "ok": true,
  "payload": {
    "chartId": "CHART-CTRL-002",
    "layout": {},
    "components": [],
    "data": {}
  }
}
```

이 API는 Chart Viewer와 Chart Builder preview가 공통으로 사용한다.

```text
Chart Viewer
  -> runtime-render-payload 조회
  -> 읽기 전용 렌더링

Chart Builder Preview
  -> 현재 편집 중인 임시 payload 렌더링
  -> 저장 전 검증
```

## 14. 사용자 작업 흐름

### 14.1 기존 chart 수정

```text
1. chart 목록에서 CHART-CTRL-002 선택
2. Builder 열기
3. 기존 preset과 component 배치 로딩
4. side_bottom 영역 높이 조정
5. state_timeline config 수정
6. preview 확인
7. 저장
```

### 14.2 새 chart 생성

```text
1. 새 chart 생성 클릭
2. chart id와 이름 입력
3. layout preset 선택
4. component palette에서 component 배치
5. data binding 설정
6. preview 확인
7. 저장
```

### 14.3 Component 교체

```text
1. main area의 detector_statistic_view 선택
2. replace component 클릭
3. trend_line 선택
4. 기존 data binding을 가능한 범위에서 유지
5. 누락 binding 보정
6. preview 확인
```

## 15. UI 상태

Builder는 다음 상태를 명확히 표시한다.

| 상태 | 표시 |
|---|---|
| clean | 저장된 상태와 동일 |
| dirty | 저장되지 않은 변경 있음 |
| invalid | 저장 불가. validation error 존재 |
| preview_loading | preview 생성 중 |
| save_running | 저장 중 |
| save_failed | 저장 실패 |

저장 버튼은 `dirty=true`이고 `invalid=false`일 때만 활성화한다.

## 16. 검증 메시지

검증 메시지는 사용자가 바로 고칠 수 있게 구체적이어야 한다.

예:

```text
bar_chart in side_top:
value_field가 설정되지 않았습니다.
Properties > Data Binding에서 numeric field를 선택하세요.
```

```text
event_marker in main:
overlay 대상 scale provider가 없습니다.
main area에 trend_line 또는 detector_statistic_view를 먼저 배치하세요.
```

## 17. MVP 구현 범위

첫 구현은 다음으로 제한한다.

```text
component palette 표시
default_3_panel layout 표시
area 선택
component 선택 후 area에 추가
component 삭제
Properties에서 config JSON 직접 편집
Properties에서 data binding JSON 직접 편집
preview 렌더링
저장/불러오기
runtime render payload 조회
runtime renderer로 chart 출력
```

Drag and drop, schema 기반 form, replace component, version diff는 다음 단계로 둔다.

## 18. 이후 확장

MVP 이후 확장:

```text
drag and drop 배치
react-grid-layout 기반 area resize
component별 schema form 자동 생성
field type validation
layout preset 저장
chart version 관리
component reuse analytics
existing 53 charts 자동 변환
```

## 19. 결론

Chart Builder는 가능하며, 구현의 핵심은 다음 세 가지다.

```text
1. 구현된 component type 목록을 palette로 제공한다.
2. semantic area container에 component instance를 배치한다.
3. config와 data binding을 DB에 저장해 React renderer가 런타임에 완전한 chart를 복원한다.
```

이 구조를 사용하면 기존 iframe 기반 chart를 점진적으로 제거하고, DB 설정 기반의 조립형 chart 시스템으로 전환할 수 있다.

초기 build 결과는 코드 파일이 아니라 runtime render payload다.

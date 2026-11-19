# 드리프트 지표 시계열

componentType:

```text
drift_metric_timeseries
```

displayName:

```text
드리프트 지표 시계열
```

핵심 전제:

```text
이 컴포넌트는 드리프트 여부와 장기 추세를 확인하기 위한 시계열 컴포넌트다.
초/분 단위 고빈도 분석이나 실시간 스트리밍 시각화가 목적이 아니다.
서버는 시간 단위 원천 데이터와 일 단위 요약 데이터를 제공하고, UI는 일 단위 평균을 기본으로 보여준다.
시간 단위 상세 보기는 최대 7일 이내 범위에서만 허용한다.
```

목적:

```text
드리프트 탐지 지표를 시간축 시계열로 보여주고, warning/drift 이벤트를 점 또는 영역으로 표시한다.
연/월/일/시간 단위의 시간 scale 전환과 장기간 추세 확인을 지원한다.
기본은 하나의 feature를 표시하고, 필요하면 비교 feature를 같은 시간축으로 함께 표시한다.
```

문서:

- [functional_requirements.md](./functional_requirements.md): 기능 요구사항
- [ui_requirements.md](./ui_requirements.md): UI 요구사항과 시간축 tick/label 정책
- [concepts.md](./concepts.md): 핵심 개념과 용어 정리
- [state_model.md](./state_model.md): 시간 이동/범위 변경/스케일 변경 상태 모델
- [implementation_notes.md](./implementation_notes.md): 구현 메모, 후순위 기능, 참고 패턴
- [analysis_chart_integration.md](./analysis_chart_integration.md): 이벤트 분석 팝업과 재생성 차트 payload 연동 기준
- [react_implementation_design.md](./react_implementation_design.md): React 컴포넌트/상태/hook 구현 설계
- [ui_mockup.html](./ui_mockup.html): PNG 생성을 위한 HTML/SVG UI 시안
- [drift_metric_timeseries_ui_mockup.png](./drift_metric_timeseries_ui_mockup.png): UI 시안 PNG

테스트 화면:

- [../web/drift_metric_timeseries_harness.html](../web/drift_metric_timeseries_harness.html): 연단위 샘플 데이터 기반 상태 영역 동기화 테스트
- [../web/drift_metric_timeseries_demo.html](../web/drift_metric_timeseries_demo.html): 실제 UI 데모

핵심 설계:

```text
raw point 전체 표시가 아니라 bucketed aggregate series를 기본 입력으로 사용한다.
서버는 1h/1d/1w/1M 등 사전 집계 데이터를 제공할 수 있다.
UI는 현재 visible range와 plot width에 맞춰 추가 압축할 수 있다.
x축 tick label은 visible range와 plot width 기준으로 자동 선택하고, 겹치면 tick 수를 줄인다.
warning과 drift는 색상과 marker/region 강도로 구분한다.
시간 범위, 축 스케일, 집계 단위, 전체 기간 안의 현재 위치를 UI에 항상 노출한다.
사용자의 시간 이동/범위 조정/스케일 변경은 단일 상태 모델을 통해 정규화한 뒤 렌더링한다.
다중 feature 비교에서는 time state를 하나만 공유하고 feature별 y축/이벤트/threshold는 독립적으로 관리한다.
```
